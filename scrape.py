import datetime
import requests
import yaml

TYPE = 41427239949909  # id of iap events
URL = "http://calendar.mit.edu/api/2/events"
DEBUG = False


def iap_year():
    # the next iap is either this year or next year
    now = datetime.datetime.now()
    if now < datetime.datetime(now.year, 1, 31):
        return now.year
    return now.year + 1


# extremely and incredibly cursed
class Wrapper:
    def __init__(self, dict_ = None):
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
    year = iap_year()
    params = {
        "type": TYPE,
        "start": f"{year}-01-01",
        "end": f"{year}-01-31",
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


# turn event into front matter
def parse_front_matter(event):
    front_matter = {}
    front_matter["title"] = event.title
    front_matter["link"] = event.url
    if event.experience == "virtual":
        front_matter["location"] = "Virtual"
    else:
        front_matter["location"] = ", ".join(filter(None, [event.location, event.location_name, event.room_number]))
    front_matter["contact"] = event.custom_fields.contact_email
    front_matter["localist_url"] = event.localist_url
    front_matter["sessions"] = []
    for wrapper in event.event_instances:
        instance = wrapper.event_instance
        front_matter["sessions"].append({
            "start": instance.start,
            "end": instance.end
        })
    front_matter["date"] = front_matter["sessions"][0]["start"]
    front_matter["interests"] = []
    for interest in event.filters.event_events_by_interest:
        if "IAP" not in interest.name:
            front_matter["interests"].append(interest.name)
    front_matter["types"] = []
    for type_ in event.filters.event_types:
        front_matter["types"].append(type_.name)
    front_matter["sponsors"] = []
    for sponsor in event.departments:
        front_matter["sponsors"].append(sponsor.name)
    for group in event.groups:
        front_matter["sponsors"].append(group.name)
    for category in ["interests", "types", "sponsors"]:
        if not front_matter[category]:
            front_matter[category] = "Other"
    return front_matter

# format event given per localist api
def format_event(event):
    res = []
    res.append("---")
    res.append(yaml.dump(parse_front_matter(event)))
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
    with open("./_data/meta.yaml", "w") as file:
        file.write(f"last_update: {datetime.datetime.now()}")
