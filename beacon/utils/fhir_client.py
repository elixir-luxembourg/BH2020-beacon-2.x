import logging

import aiohttp
from aiohttp.web_exceptions import HTTPError

from .. import conf

LOG = logging.getLogger(__name__)

ontology_mappings = {
    "SNO": "http://snomed.info/sct"
}

gender_mappings = {
    '0000383': 'female',
    '0000384': 'male'
}


class FHIRConnection:
    fhir_pool = None

    def __init__(self):
        self.fhir_base_url = f"{conf.fhir_schema}://{conf.fhir_host}:{conf.fhir_port}/{conf.fhir_base_endpoint}"

    def asyncgen_execute(self, func):
        async def inner(*args, **kwargs):
            headers = {
                'Accept': 'application/fhir+json'
            }
            async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
                try:
                    response = await func(session, self.fhir_base_url, *args, **kwargs)
                    LOG.debug(f"Response status: {response.status}")
                except HTTPError as http_err:
                    LOG.error(f"HTTP error occurred: {http_err}")
                except Exception as err:
                    LOG.error(f"An error ocurred: {err}")
                else:
                    json_response = await response.json()
                    if json_response.get('resourceType') == 'Bundle':
                        for resource in json_response.get('entry', []):
                            yield resource
                    else:
                        yield json_response

        return inner


pool = FHIRConnection()


@pool.asyncgen_execute
async def fetch_biosamples_by_biosample(session, fhir_base_url, qparams_db, datasets, authenticated):
    filters = qparams_db.filters

    type_params = []
    for f in filters:
        ont, value = f.split(':')
        type_params.append(f"{ontology_mappings[ont]}|{value}")

    url = f"{fhir_base_url}/Specimen?type={','.join(type_params)}"

    return await session.request(method='GET', url=url)


@pool.asyncgen_execute
async def fetch_biosamples_by_individuals(session, fhir_base_url, qparams_db, datasets, authenticated):
    individual_id = qparams_db.targetIdReq

    url = f"{fhir_base_url}/Specimen"
    if individual_id is not None:
        url = f"{url}?patient=Patient/{individual_id}"
    LOG.debug("Querying url %s", url)

    return await session.request(method='GET', url=url)


@pool.asyncgen_execute
async def fetch_individuals_by_individuals(session, fhir_base_url, qparams_db, datasets, authenticated):
    filters = qparams_db.filters
    individual_id = qparams_db.targetIdReq

    url = f"{fhir_base_url}/Patient"

    if individual_id:
        url = f"{url}/{individual_id}"
    elif filters and len(filters) > 0:  # only if we're not getting the exact patient we apply the gender filter
        url = f"{url}?gender={','.join(filters)}"
    LOG.debug("Querying url %s", url)
    return await session.request(method='GET', url=url)
