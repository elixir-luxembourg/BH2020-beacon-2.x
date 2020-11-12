import logging

import aiohttp
from aiohttp.web_exceptions import HTTPError

from .. import conf

LOG = logging.getLogger(__name__)

ontology_mappings = {
    "SNO": "http://snomed.info/sct"
}


class FHIRConnection:
    fhir_pool = None

    def __init__(self):
        self.fhir_base_url = f"{conf.fhir_schema}://{conf.fhir_host}:{conf.fhir_port}/{conf.fhir_base_endpoint}"
        # self.fhir_base_url = f"http://hapi.fhir.org:80/baseR4"

    def asyncgen_execute(self, func):
        async def inner(*args, **kwargs):
            headers = {
                'Accept': 'application/fhir+json'
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                async for obj in func(session, self.fhir_base_url, *args, **kwargs):
                    yield obj

        return inner

    # async def connection(self):
    #     if self.fhir_pool is None:
    #         await self.connect()
    #     return self.fhir_pool


pool = FHIRConnection()


@pool.asyncgen_execute
async def fetch_biosamples_by_biosample(session, fhir_base_url, qparams_db, datasets, authenticated):
    filters = qparams_db.filters

    type_params = []
    for f in filters:
        ont, value = f.split(':')
        type_params.append(f"{ontology_mappings[ont]}|{value}")

    url = f"{fhir_base_url}/Specimen?type={','.join(type_params)}"

    try:
        response = await session.request(method='GET', url=url)
        response.raise_for_status()
        LOG.debug(f"Response status ({url}): {response.status}")
    except HTTPError as http_err:
        LOG.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        LOG.error(f"An error ocurred: {err}")
    else:
        resources = await response.json()
        for resource in resources.get('entry'):
            yield resource
