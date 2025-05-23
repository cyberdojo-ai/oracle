import httpx
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime


from src.db.database import SessionLocal
from src import utils
from src.db import crud, schemas
from src.cron import Event
import re


class SansEduScraper:
    """
    Basic web scraper for https://isc.sans.edu/diaryarchive.html using httpx and BeautifulSoup.
    """

    def __init__(
        self,
        url="https://isc.sans.edu/diaryarchive.html",
        query_params={},
    ) -> None:
        self.url = url
        self.query_params = query_params
        self.page_content = None
        self.soup = None
        self.sources: list[schemas.SourceCreate] = []

    async def fetch_page(self):
        """
        Fetches the HTML content of the target page using httpx.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.url,
                params=self.query_params
            )
            response.raise_for_status()
            print(response.request.url)
            self.page_content = response.text
        return self.page_content


    def parse_html(self):
        """
        Parses the fetched HTML content with BeautifulSoup.
        """
        if self.page_content is None:
            self.fetch_page()
        self.soup = BeautifulSoup(self.page_content, "html.parser")
        return self.soup

    def extract_urls(self):
        """
        Extracts urls from the <a> tag elements in the <h2> with class card-tile from the <div> with class isc-card
        """
        urls = []
        for card in self.soup.find_all("div", class_="isc-card"):
            for body in card.find_all("div", class_="card-body"):
                for title in body.find_all("h2", class_="card-title"):
                    for link in title.find_all("a"):
                        href = link.get("href")
                        if href and href.startswith("http"):
                            urls.append(href)
                        else:
                            # Handle relative URLs
                            base_url = self.url.rstrip("/")
                            full_url = f"{base_url}/{href.lstrip('/')}"
                            urls.append(full_url)
        # Remove duplicates
        urls = list(set(urls))
        return urls

    async def fetch_sources(self, urls: list[str]) -> list[schemas.SourceCreate]:
        """
        Fetches the content of the diaries from the extracted URLs.
        """
        self.sources: list[schemas.SourceCreate] = []
        async with httpx.AsyncClient() as client:
            for url in urls:
                response = await client.get(url)
                response.raise_for_status()
                diary_content = response.text
                # Process diary content as needed
                print(f"Fetched diary from - {url}")
                soup = BeautifulSoup(diary_content, "html.parser")
                article = soup.find("article")
                title = article.find("h1").text
                content = article.find("div", class_="diarybody").text.lstrip()
                diary_header = article.find("div", class_="diaryheader").text
                try:
                    published_date_match = re.search(r"Published:\s*(\d{4}-\d{2}-\d{2})", diary_header)
                    published_date: date | None = date.fromisoformat(published_date_match.group(1)) if published_date_match else None
                except ValueError:
                    published_date = None

                try:
                    updated_on_match = re.search(r"Last Updated:\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \w+)", diary_header)
                    updated_on: datetime | None = datetime.strptime(updated_on_match.group(1), "%Y-%m-%d %H:%M:%S %Z") if updated_on_match else None
                except ValueError:
                    updated_on = None

                self.sources.append(schemas.SourceCreate(
                    title=title,
                    url=url,
                    content=content,
                    fetched_on=utils.current_utc_time(),
                    published_on=published_date,
                    updated_on=updated_on,
                ))
        return self.sources

    async def run(
        self,
        db_session: AsyncSession,
    ) -> None:
        """
        Main method to run the scraper.
        """
        await self.fetch_page()
        self.parse_html()
        print("Page fetched and parsed.")
        print("Extracting URLs...")
        urls = self.extract_urls()
        print(f"URLs extracted - {len(urls)} URLs found.")

        if not urls:
            print("No URLs found.")
            return

        # Filter out URLs that are already in the database
        existing_sources = await crud.async_base_get_source(
            db_session,
            urls=urls,
        )
        if existing_sources:
            print(f"Found {len(existing_sources)} existing sources in the database.")
            existing_urls = [source.url for source in existing_sources]
            urls = [url for url in urls if url not in existing_urls]
            print(f"Filtered out {len(existing_urls)} existing URLs.")


        print(f"Fetching {len(urls)} urls...")
        sources = await self.fetch_sources(urls)
        print(f"Fetched {len(sources)} urls.")

async def enrichment_job_async(
    name: str,
    description: str,
    this_month: bool = True,
    last_month: bool = False,
    this_year: bool = False,
    last_year: bool = False,
) -> None:
    """
    This function is a placeholder for the enrichment job.
    It currently does not perform any operations.
    """
    db_session: AsyncSession = SessionLocal()

    db_job = await crud.async_base_create_enrichment_job(
        db_session,
        schemas.EnrichmentJobCreate(
            name=name,
            description=description,
            status=schemas.JobStatus.PENDING,
            started_at=utils.current_utc_time(),
        ),
    )

    print(f"Enrichment job - {db_job.id} - is running...")
    current_time = utils.current_utc_time()
    if this_year:
        for i in range(1, current_time.month + 1):
            sans_scraper = SansEduScraper(
                query_params={
                    "year": current_time.year,
                    "month": i,
                },
            )
            await sans_scraper.run(db_session)

            sources: list[schemas.SourceCreate] = sans_scraper.sources
            if not sources:
                print("No new sources found.")
            else:
                # Create sources in the database
                for source in sources:
                    source.enrichment_job_id = db_job.id
                    await crud.async_base_create_source(db_session, source)

    if last_year:
        for i in range(1, 13):
            sans_scraper = SansEduScraper(
                query_params={
                    "year": current_time.year - 1,
                    "month": i,
                },
            )
            await sans_scraper.run(db_session)

            sources: list[schemas.SourceCreate] = sans_scraper.sources
            if not sources:
                print("No new sources found.")
            else:
                # Create sources in the database
                for source in sources:
                    source.enrichment_job_id = db_job.id
                    await crud.async_base_create_source(db_session, source)

    if this_month:
        sans_scraper = SansEduScraper(
            query_params={
                "year": current_time.year,
                "month": current_time.month,
            },
        )
        await sans_scraper.run(db_session)


        sources: list[schemas.SourceCreate] = sans_scraper.sources
        if not sources:
            print("No new sources found.")
        else:
            # Create sources in the database
            for source in sources:
                source.enrichment_job_id = db_job.id
                await crud.async_base_create_source(db_session, source)

    if last_month:
        query_params = {
            "year": current_time.year if current_time.month > 1 else current_time.year - 1,
            "month": current_time.month - 1 if current_time.month > 1 else 12,
        }
        sans_scraper = SansEduScraper(
            query_params=query_params,
        )
        await sans_scraper.run(db_session)

        sources: list[schemas.SourceCreate] = sans_scraper.sources
        if not sources:
            print("No new sources found.")
        else:
            # Create sources in the database
            for source in sources:
                source.enrichment_job_id = db_job.id
                await crud.async_base_create_source(db_session, source)

    db_job = await crud.async_base_update_enrichment_job(
        db_session,
        db_job,
        schemas.EnrichmentJobUpdate(
            status=schemas.JobStatus.COMPLETED,
            finished_at=utils.current_utc_time(),
        ),
    )

    print(f"Enrichment job - {db_job.id} - finished.")

cron_events: list[Event] = [
    Event( # Run every hour
        action=enrichment_job_async,
        minute=0,
        kwargs={
            "name": "ICS - Sans - Hourly job",
            "description": "Run every hour",
            "this_month": True,
            "last_month": False,
            "this_year": False,
            "last_year": False,
        },
    ),
    Event( # Run on the first day of every month at midnight
        action=enrichment_job_async,
        minute=0,
        hour=0,
        day=1,
        kwargs={
            "name": "ICS - Sans - Monthly job",
            "description": "Run on the first day of every month at midnight",
            "this_month": False,
            "last_month": True,
        },
    ),
]
