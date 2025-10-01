from datetime import timedelta
from temporalio import activity
import aiohttp

# Assuming services and storage are in the python path
from services.onedrive.client import (
    list_notebooks,
    list_sections,
    list_pages,
    get_page_content,
)
from services.onedrive.parser import extract_note_points
from storage.memory_store import db_adapter


@activity.defn(name="sync_onenote")
async def sync_onenote() -> str:
    """
    Syncs OneNote data to Neo4j.

    This activity fetches all notebooks, sections, and pages from OneDrive,
    parses the content for note points, and upserts everything into the
    Neo4j database.
    """
    await db_adapter.connect()
    try:
        async with aiohttp.ClientSession() as session:
            notebooks = await list_notebooks(session)
            activity.logger.info(f"Found {len(notebooks)} notebooks.")

            for nb in notebooks:
                notebook_id = nb["id"]
                await db_adapter.upsert_notebook(notebook_id, nb["displayName"])

                sections = await list_sections(session, notebook_id)
                activity.logger.info(
                    f"Found {len(sections)} sections in notebook {notebook_id}."
                )
                for sec in sections:
                    section_id = sec["id"]
                    await db_adapter.upsert_section(
                        section_id, sec["displayName"], notebook_id
                    )

                    pages = await list_pages(session, section_id)
                    activity.logger.info(
                        f"Found {len(pages)} pages in section {section_id}."
                    )
                    for pg in pages:
                        page_id = pg["id"]
                        await db_adapter.upsert_page(page_id, pg["title"], section_id)

                        html_content = await get_page_content(session, page_id)
                        points = extract_note_points(html_content)
                        activity.logger.info(
                            f"Found {len(points)} note points in page {page_id}."
                        )

                        for idx, pt in enumerate(points):
                            point_id = f"{page_id}-{idx}"
                            await db_adapter.upsert_note_point(
                                point_id, pt["type"], pt["text"], page_id
                            )
        return "OneNote sync complete"
    finally:
        await db_adapter.close()


# The configuration for the activity is usually set when it's executed
# in the workflow, but we can define defaults here if needed.
# For example, using a decorator argument:
# @activity.defn(name="sync_onenote", start_to_close_timeout=timedelta(minutes=20))
# The retry policy is also typically set in the workflow execution call.
