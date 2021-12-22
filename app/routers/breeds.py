from bson import ObjectId, json_util
from fastapi import APIRouter
from dotenv import load_dotenv
from decouple import config
from typing import Union
import requests

load_dotenv('.env')
router = APIRouter()
api_key = config('DB_API_KEY')

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers': '*',
    'api-key': api_key
}

general_payload = {
    "database": "db",
    "dataSource": "breeds-counter",
}

base_url = "https://data.mongodb-api.com/app/data-glklp/endpoint/data/beta/action"


def post_request(collection='breeds_collection', action: str = '', payload=None):
    if payload is None:
        payload = {}

    url = f'{base_url}/{action}'
    payload['collection'] = collection

    res = requests.post(url, data=json_util.dumps(payload), headers=headers)

    if not res.ok:
        print('Incorect request')
        return

    return res


def get_one_info_from_all_breeds(info_name: str) -> Union[None, list]:
    """
    :param info_name: Le nom de l'info
    :return: Retourne la liste d'une info specifique pour toutes les races
    """
    try:
        res = requests.get('https://api.thecatapi.com/v1/breeds').json()
        breeds_info = [i[info_name] for i in res]
        return breeds_info
    except KeyError:
        print(f'{info_name} unknown in api')


def get_all_info_from_one_breeds(breed_id: str) -> Union[None, dict]:
    """
    :param breed_id: L'id du chat dont l'on veut récupérer ses info
    :return: le resultat de la requete à l'api
    """
    url = f'https://api.thecatapi.com/v1/breeds/search?q={breed_id}'
    res = requests.get(url)

    if not res.ok:
        return

    return res.json()[0]


def get_one_image(image_id: str) -> Union[None, str]:
    url = f'https://api.thecatapi.com/v1/images/{image_id}'
    res = requests.get(url)

    if not res.ok:
        return

    return res.json()['url']


def get_multiples_images_from_one_breeds(breed_id: str, base_image_id: str, limit: int) -> Union[None, list]:
    url = f'https://api.thecatapi.com/v1/images/search?breed_id={breed_id}&limit={limit + 1}'
    res = requests.get(url)
    images = [i['url'] for i in res.json()]
    base_image_url = get_one_image(base_image_id)

    if not base_image_url:
        return

    if base_image_url in images:
        images.remove(base_image_url)
    else:
        images.pop(-1)

    return images


@router.get('/ping')
async def ping():
    """
    Test si la db est connecté
    :return: 'ping' : 'pong'
    """

    general_payload["filter"] = {
        "_id": ObjectId('618594c58955defb6f2d9327')
    }

    res = post_request(collection='db_testing', action='findOne', payload=general_payload)

    return {'ping': res.json()['document']['ping']}


@router.get('/names')
async def get_breeds_name():
    """
    :return: La liste des noms des races de chats
    """
    breeds_name = get_one_info_from_all_breeds('name')

    if not breeds_name:
        return 'Internal error'
    return breeds_name


@router.get('/popular')
async def get_popular_breeds_info(limit: int = 4):
    """
    :param limit: Le nombre limite de résultats qu'on veut obtenir
    :return: La description, l'image et le nom des x races demandé avec :limit les plus populaire dans la db
    """
    general_payload['filter'] = {}
    general_payload['sort'] = {
        "views": -1
    }

    res = post_request(
        action='find',
        payload=general_payload
    ).json()

    raw_breeds = res['documents'][:limit]
    breeds = [breed.get('breed_id') for breed in raw_breeds]

    return breeds


@router.get('/{breed_id}')
async def get_breed_info(breed_id):
    raw_breed = get_all_info_from_one_breeds(breed_id)
    image_id = raw_breed.get('reference_image_id')

    breed = {
        'name': raw_breed.get('name'),
        'description': raw_breed.get('description'),
        'temparament': raw_breed.get('temperament'),
        'origin': raw_breed.get('origin'),
        'lifeSpan': raw_breed.get('life_span'),
        'adaptability': raw_breed.get('adaptability'),
        'affection': raw_breed.get('affection'),
        'childFriendly': raw_breed.get('childFriendly'),
        'grooming': raw_breed.get('grooming'),
        'intelligence': raw_breed.get('intelligence'),
        'healhIssues': raw_breed.get('health_issues'),
        'socialNeeds': raw_breed.get('social_needs'),
        'strangerFriendly': raw_breed.get('stranger_friendly'),
        'mainImageUrl': get_one_image(image_id),
        'imagesUrls': get_multiples_images_from_one_breeds(
            breed_id=breed_id,
            base_image_id=image_id,
            limit=8
        )
    }

    return breed


@router.post('/{breed_id}/counter')
async def increase_breed_counter(breed_id):
    """
    :param breed_id: L'id du chat où l'on veut augmenter son compteur
    :return: Status de la requête
    """
    breeds_id = get_one_info_from_all_breeds('id')

    general_payload['filter'] = {
        "breed_id": breed_id
    }

    db_ref = post_request(
        action='findOne',
        payload=general_payload
    )

    if not db_ref.json()['document']:
        db_ref = None

    if not breeds_id:
        return 'Internal error'
    elif breed_id not in breeds_id:
        return f'{breed_id} unknow in api'

    if db_ref:
        general_payload['filter'] = {'breed_id': breed_id}
        general_payload['update'] = {"$inc": {'views': 1}}

        result = post_request(
            action='updateOne',
            payload=general_payload
        )

        return f'{breed_id} was corectly updated' if result else 'Internal Error'
    else:
        general_payload['document'] = {
            "breed_id": breed_id,
            "views": 1
        }

        result = post_request(
            action='insertOne',
            payload=general_payload
        )

        return f'{breed_id} was corectly inserted' if result else 'Internal Error'


if __name__ == '__main__':
    pass
