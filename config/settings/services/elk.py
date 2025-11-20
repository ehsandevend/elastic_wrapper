from typing import AsyncGenerator
import logging
from elasticsearch import AsyncElasticsearch
from elastic_transport import ConnectionError, ConnectionTimeout

from config.settings.integrations_config import ELKConfig
from shared.enums import ElkClientTypeChoices


logger = logging.getLogger(__name__)


class ElasticsearchManager:
    """
    Manager for Elasticsearch clients with separate read and write instances.

    This ensures proper separation of concerns and security boundaries:
    - Read client: Limited to search/get operations
    - Write client: Full access for CRUD operations
    """

    _instance: "ElasticsearchManager | None" = None
    _read_client: AsyncElasticsearch | None = None
    _write_client: AsyncElasticsearch | None = None
    _is_initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self) -> None:
        if self._is_initialized:
            logger.warning("Elasticsearch clients already initialized")
            return

        try:
            self._read_client = await self._create_client(
                client_type=ElkClientTypeChoices.READ,
                user=ELKConfig.ELASTIC_READ_USER,
                password=ELKConfig.ELASTIC_READ_PASSWORD,
            )

            self._write_client = await self._create_client(
                client_type=ElkClientTypeChoices.WRITE,
                user=ELKConfig.ELASTIC_WRITE_USER,
                password=ELKConfig.ELASTIC_WRITE_PASSWORD,
            )

            info = await self._read_client.info()
            logger.info(
                f"Connected to Elasticsearch cluster: {info['cluster_name']} "
                f"(version {info['version']['number']})"
            )
            logger.info("✓ Read-only client initialized")
            logger.info("✓ Read-write client initialized")

            self._is_initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch clients: {e}")
            await self._cleanup_clients()
            raise

    @staticmethod
    async def _create_client(
        client_type: ElkClientTypeChoices,
        user: str = None,
        password: str = None,
    ) -> AsyncElasticsearch:
        client = AsyncElasticsearch(
            hosts=[f"http://{ELKConfig.ELASTIC_HOST}:{ELKConfig.ELASTIC_PORT}"],
            basic_auth=(
                (user, password)
                if user and password
                else None
            ),
            verify_certs=False,
            max_retries=ELKConfig.ELASTIC_MAX_RETRIES,
            retry_on_timeout=True,
            request_timeout=ELKConfig.ELASTIC_TIMEOUT,
            http_compress=True,
            connections_per_node=ELKConfig.ELASTIC_CONNECTIONS_PER_NODE,
            sniff_on_start=False,
        )

        if not await client.ping():
            await client.close()
            raise ConnectionError(
                f"Failed to ping Elasticsearch cluster with {client_type.value} client"
            )

        return client

    async def get_read_client(self) -> AsyncElasticsearch:
        if not self._is_initialized or self._read_client is None:
            raise RuntimeError(
                "Elasticsearch read client not initialized. "
                "Call initialize() during application startup."
            )
        return self._read_client

    async def get_write_client(self) -> AsyncElasticsearch:
        if not self._is_initialized or self._write_client is None:
            raise RuntimeError(
                "Elasticsearch write client not initialized. "
                "Call initialize() during application startup."
            )
        return self._write_client

    async def health_check(self) -> dict[str, bool]:
        read_healthy = False
        write_healthy = False

        if self._read_client:
            try:
                read_healthy = await self._read_client.ping()
            except Exception as e:
                logger.error(f"Read client health check failed: {e}")

        if self._write_client:
            try:
                write_healthy = await self._write_client.ping()
            except Exception as e:
                logger.error(f"Write client health check failed: {e}")

        return {
            "read_client": read_healthy,
            "write_client": write_healthy
        }

    async def _cleanup_clients(self) -> None:
        if self._read_client:
            await self._read_client.close()
            self._read_client = None
        if self._write_client:
            await self._write_client.close()
            self._write_client = None

    async def close(self) -> None:
        if self._read_client:
            await self._read_client.close()
            logger.info("✓ Read client closed")
            self._read_client = None

        if self._write_client:
            await self._write_client.close()
            logger.info("✓ Write client closed")
            self._write_client = None

        self._is_initialized = False


es_manager = ElasticsearchManager()


async def get_read_es_client() -> AsyncGenerator[AsyncElasticsearch, None]:
    client = await es_manager.get_read_client()

    try:
        await client.ping()
    except (ConnectionError, ConnectionTimeout) as e:
        logger.error(f"Read client not available: {e}")
        raise ConnectionError("Elasticsearch read service unavailable") from e

    yield client


async def get_write_es_client() -> AsyncGenerator[AsyncElasticsearch, None]:
    client = await es_manager.get_write_client()

    try:
        await client.ping()
    except (ConnectionError, ConnectionTimeout) as e:
        logger.error(f"Write client not available: {e}")
        raise ConnectionError("Elasticsearch write service unavailable") from e

    yield client
