import requests

TYPE = 102809  # id of iap events
URL = "http://calendar.mit.edu/api/2/events"
YEAR = 2022
DEBUG = False


# extremely and incredibly cursed
class Wrapper:
    def __init__(self, dict_: dict[str, str] = None):
        self.dict = dict_ or {}

    def get(self, name):
        res = self.dict.get(name, "")
        if isinstance(res, dict):
            return Wrapper(res)
        elif isinstance(res, list):
            return list(map(Wrapper, res))  # type: ignore
        elif res is None:
            return ""
        else:
            return res

    def __getattr__(self, name):
        return self.get(name)

    def __getitem__(self, name):
        return self.get(name)


# get and collect all iap events
# events are returned per https://developer.localist.com/doc/api#event-json
def get_events():
    params = {
        "type": TYPE,
        "start": f"{YEAR}-01-01",
        "end": f"{YEAR}-01-31",
        "page": 1,
        "pp": 100 if not DEBUG else 10,
    }
    req = requests.get(URL, params=params).json()
    n_pages = req["page"]["total"]
    res = req["events"]
    if DEBUG:
        return res
    for page in range(2, n_pages + 1):
        params["page"] = page
        req = requests.get(URL, params=params).json()
        res.extend(req["events"])
    return res


# peel the "events" key, and merge instances together if they have the same id
def merge_events(events):
    result = {}
    for wrapper in events:
        event = wrapper["event"]
        id_ = event["id"]
        if id_ not in result:
            result[id_] = event
        else:
            result[id_]["event_instances"].extend(event["event_instances"])
    return result


# format event given per localist api
def format_event(event):
    # TODO: use an actual yaml dumper or something
    res = []
    res.append("---")
    res.append(f"title: '{event.title}'")
    res.append(f"url: '{event.url}'")
    res.append(
        f"location: '{( event.location + event.room_number ) or event.location_name}'"
    )
    res.append("sessions:")
    for wrapper in event.event_instances:
        instance = wrapper.event_instance
        res.append(f"  - start: '{instance.start}'")
        res.append(f"    end: '{instance.end}'")
    res.append(f"contact: '{event.custom_fields.contact_email}'")
    res.append("interests:")
    for interest in event.filters.event_events_by_interest:
        res.append(f"  - '{interest.name}'")
    res.append("types:")
    for type_ in event.filters.event_types:
        res.append(f"  - '{type_.name}'")
    res.append("sponsors:")
    for sponsor in event.departments:
        res.append(f"  - '{sponsor.name}'")
    for group in event.groups:
        res.append(f"  - '{group.name}'")
    res.append(f"localist_url: '{event.localist_url}'")
    res.append("---")
    res.append(event.description)
    return "\n".join(res)


if __name__ == "__main__":
    for unwrapped in merge_events(get_events()).values():
        event = Wrapper(unwrapped)
        path = f"./_events/{event.urlname}.md"
        with open(path, "w") as file:
            file.write(format_event(event))
        if DEBUG:
            break
