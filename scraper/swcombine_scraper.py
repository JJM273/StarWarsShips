"""scraper for swcombine ship data"""

# Standard Imports
# Third Party Imports
import requests
import bs4
# Local Imports



def parse_ship_sublist(items: bs4.ResultSet[bs4.Tag],split: bool = False, delim: str = None) -> list[str|list[str]]:
    result: list = []
    for tag in items:
        row = tag.text
        if not split:
            result.append(row)
        else:
            result.append(row.split(delim))
    return result


def parse_ships(ships_soup: bs4.BeautifulSoup, **kwargs):
    for ship in ships_soup.find_all(class_='entity-overview'):
        ship_specs = {
            'Propulsion': parse_ship_sublist(ship.find(class_='rdbox propulsion').find_all('li'),split=True,delim=": "),
            'Dimensions': parse_ship_sublist(ship.find(class_='rdbox dimensions').find_all('li'),split=True,delim=": "),
            'Cargo': parse_ship_sublist(ship.find(class_='rdbox cargo').find_all('li'),split=True,delim=": "),
            'Role': parse_ship_sublist(ship.find(class_='rdbox role').find_all('li')),
            'Weapons': parse_ship_sublist(ship.find(class_='rdbox weapons').find_all('li'),split=True,delim=": "),
            'Defenses': parse_ship_sublist(ship.find(class_='rdbox defenses').find_all('li'),split=True,delim=": "),
            'Electronics': parse_ship_sublist(ship.find(class_='rdbox electronics').find_all('li'),split=True,delim=": "),
            'Production': parse_ship_sublist(ship.find(class_='rdbox production').find_all('li'),split=True,delim=": "),
            'Affiliations': parse_ship_sublist(ship.find(class_='rdbox affiliations').find_all('li')),
            }
        ship_specs.update(kwargs)
        yield (ship.find(class_='head').find('span').text, ship_specs)

def main() -> None:
    ships_dict = {}
    ship_pages = ["https://www.swcombine.com/rules/?Capital_Ships",
                  "https://www.swcombine.com/rules/?Super_Capitals",
                  "https://www.swcombine.com/rules/?Frigates",
                  "https://www.swcombine.com/rules/?Corvettes",
                  "https://www.swcombine.com/rules/?Heavy_Freighters",
                  "https://www.swcombine.com/rules/?Light_Freighters",
                  "https://www.swcombine.com/rules/?Gunboats",
                  "https://www.swcombine.com/rules/?Fighters",
                  ]
    
    for page in ship_pages:
        ship_html = requests.get(page, timeout=30)
        ship_soup = bs4.BeautifulSoup(ship_html.content,'html.parser')
        ships_dict.update(ship for ship in parse_ships(ship_soup,Class=page.rsplit(sep="?",maxsplit=1)[1]))

if __name__ == '__main__':
    main()