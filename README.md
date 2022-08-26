# gsb-ticketing

Django-powered web application for the 2023 Girton Spring Ball Ticketing platform.

## Development

1. Create a virtual environment: `python3 -m venv .venv`
2. Activate the environment: `. .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Set up pre-commit: `pre-commit install`
5. Source required variables: `. app/dev.sh`
6. Run local development server: `python3 manage.py runserver`

### Main dependencies

- Django

## Production

TBD

### girtifier

Verifies that a list of Cambridge emails meet these requirements: current student + current member of Girton College.

Usage: `python3 girtifier.py -h` to find out.

## Resources

- [Single app project](https://zindilis.com/posts/django-anatomy-for-single-app/)
- [Useful prod setup](https://www.oreilly.com/library/view/lightweight-django/9781491946275/ch01.html)

## License

MIT

## Credits

Matias Silva 2022
