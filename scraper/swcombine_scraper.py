"""scraper for swcombine ship data"""

# Standard Imports
# Third Party Imports
import pandas as pd
import requests
import bs4
# Local Imports

def get_category_sublist(ship: bs4.Tag, li: str = 'li', **kwargs) -> bs4.ResultSet[bs4.Tag]:
    results = ship.find(**kwargs)
    if results is None:
        return results
    return results.find_all(li)

def parse_ship_sublist(ship: bs4.Tag,split: bool = False, delim: str = None, li: str = 'li', **kwargs) -> list[str]|dict[str,str]:
    items = get_category_sublist(ship, li, **kwargs)
    result: dict = {}
    if items is None:
        return result
    if not split:
        result: list = []
        for tag in items:
            row = tag.text
            result.append(row)
    else:
        for tag in items:
            row = tag.text
            row = row.split(delim,maxsplit=1)
            if len(row) == 2:
                result.update({row[0] : row[1]})
            elif len(items) == 1:
                result = [row]
                break
    return result


def parse_ships(ships_soup: bs4.BeautifulSoup, **kwargs):
    for ship in ships_soup.find_all(class_='entity-overview'):
        ship_specs = {
            'Propulsion': parse_ship_sublist(ship, class_='rdbox propulsion',split=True,delim=": "),
            'Dimensions': parse_ship_sublist(ship, class_='rdbox dimensions',split=True,delim=": "),
            'Cargo': parse_ship_sublist(ship,class_='rdbox cargo',split=True,delim=": "),
            'Role': parse_ship_sublist(ship,class_='rdbox role'),
            'Weapons': parse_ship_sublist(ship,class_='rdbox weapons',split=True,delim=": "),
            'Defenses': parse_ship_sublist(ship,class_='rdbox defenses',split=True,delim=": "),
            'Electronics': parse_ship_sublist(ship,class_='rdbox electronics',split=True,delim=": "),
            'Production': parse_ship_sublist(ship,class_='rdbox production',split=True,delim=": "),
            'Affiliations': parse_ship_sublist(ship,class_='rdbox affiliations'),
            }
        ship_specs.update(kwargs)
        yield (ship.find(class_='head').find('span').text, ship_specs)

def get_ship_data(ship_urls: list[str]):
    ships_dict = {}
    for page in ship_urls:
        ship_html = requests.get(page, timeout=30)
        ship_soup = bs4.BeautifulSoup(ship_html.content,'html.parser')
        ships_dict.update(ship for ship in parse_ships(ship_soup,Class=page.rsplit(sep="?",maxsplit=1)[1]))
    return ships_dict    

def main() -> None:
    ship_pages = ["https://www.swcombine.com/rules/?Capital_Ships",
                  "https://www.swcombine.com/rules/?Super_Capitals",
                  "https://www.swcombine.com/rules/?Frigates",
                  "https://www.swcombine.com/rules/?Corvettes",
                  "https://www.swcombine.com/rules/?Heavy_Freighters",
                  "https://www.swcombine.com/rules/?Light_Freighters",
                  "https://www.swcombine.com/rules/?Gunboats",
                  "https://www.swcombine.com/rules/?Fighters"
                  ]

    ship_dict = get_ship_data(ship_pages)
    ship_df = pd.DataFrame(ship_dict)
    print(ship_df)
    pass


if __name__ == '__main__':
    main()
