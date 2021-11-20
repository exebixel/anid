import click
import requests
import re
from bs4 import BeautifulSoup

@click.command()
@click.argument('name')
def search_anime_by_name(name:str):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
    }
    base_url = 'https://animefire.net/pesquisar/{name}'
    url = base_url.format(name=name)
    response = requests.get(url, headers=headers)
    if response.ok:   
        search_result_html = BeautifulSoup(response.text, 'html.parser')
        show_available_animes_list(search_result_html)
    else:
        click.echo(response.status_code)
        click.echo(response.content)
        
def show_available_animes_list(search_result_html:str):
    for anime_anchor_tag in search_result_html.find_all('a',href=re.compile("todos-os-episodios")):
            anime_name = anime_anchor_tag.get('href').split('-todos-os-episodios')[0].split('animes/')[-1]
            click.echo(anime_name) 

if __name__ == '__main__':
    search_anime_by_name()