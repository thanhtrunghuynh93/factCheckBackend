from server.models.factCheck.nli_factCheck import verify


async def fact_check_by_nli(params: dict) -> dict:
    params = dict(params)
    res = verify(params["claim"])
    return res
