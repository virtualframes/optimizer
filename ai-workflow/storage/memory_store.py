import os
from neo4j import AsyncGraphDatabase

URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASS"))

class Neo4jAdapter:
    def __init__(self):
        self._driver = None

    async def connect(self):
        self._driver = AsyncGraphDatabase.driver(URI, auth=AUTH)
        await self._driver.verify_connectivity()

    async def close(self):
        if self._driver:
            await self._driver.close()

    async def _execute_query(self, query, **kwargs):
        async with self._driver.session() as session:
            await session.run(query, **kwargs)

    async def upsert_notebook(self, nb_id: str, name: str):
        query = """
        MERGE (n:Notebook {id: $notebook_id})
        SET n.name = $name
        """
        await self._execute_query(query, notebook_id=nb_id, name=name)

    async def upsert_section(self, sec_id: str, name: str, nb_id: str):
        query = """
        MERGE (s:Section {id: $section_id})
        SET s.name = $name
        WITH s
        MATCH (n:Notebook {id: $notebook_id})
        MERGE (n)-[:HAS_SECTION]->(s)
        """
        await self._execute_query(query, section_id=sec_id, name=name, notebook_id=nb_id)

    async def upsert_page(self, pg_id: str, title: str, sec_id: str):
        query = """
        MERGE (p:Page {id: $page_id})
        SET p.title = $title
        WITH p
        MATCH (s:Section {id: $section_id})
        MERGE (s)-[:HAS_PAGE]->(p)
        """
        await self._execute_query(query, page_id=pg_id, title=title, section_id=sec_id)

    async def upsert_note_point(self, pt_id: str, pt_type: str, text: str, pg_id: str):
        query = """
        MERGE (np:NotePoint {id: $point_id})
        SET np.type = $type, np.text = $text
        WITH np
        MATCH (p:Page {id: $page_id})
        MERGE (p)-[:HAS_POINT]->(np)
        """
        await self._execute_query(query, point_id=pt_id, type=pt_type, text=text, page_id=pg_id)

# Global instance
db_adapter = Neo4jAdapter()