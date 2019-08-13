# docker-weasyprint


To use, `POST` some HTML to `localhost:5001/pdf`.  The response will be a rendered pdf file.

### Health Checks

A `GET` to `localhost:5001/status` should result in an `ok` response.

A `GET` to `localhost:5001/version` should output the weasyprint version (currently `0.47`).

### Fonts

In order to make fonts available to weasyprint, simply copy them into `./fonts` and build the image.

# docker-weasyprint

This is a very simple Dockerfile based on [Alpine Linux](https://www.alpinelinux.org).

It creates a very small (105MB+) [weasyprint](https://github.com/Kozea/WeasyPrint) service.  

It uses a wsgi server by [aquavitae](https://github.com/aquavitae/docker-weasyprint) to provide weasyprint as a web service.

## Getting Started
### Development
You can run flask api localy by creating a `.env` based on `.env.example` and just run vscode debbuger by typing `f5`.
By the way, you need install weazyprint dependencies to run localy and install all libs on `requirement.txt`.

Your console output will be like this:
```shell
 * Tip: There are .env files present. Do "pip install python-dotenv" to use them.
 * Serving Flask app "app/server.py"
 * Environment: development
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
### Docker
You can create the docker just typing:
```shell
> docker-compose -f "docker-compose.yml" up -d --build
```

### Prerequisites

Docker and docker-compose.

### Motivations

Convert large html files into pdfs.

## Contributing

:construction_worker:

## Versioning

:construction_worker:

## Authors

* **Dave Rosborough** - *Initial work* - [Github](https://github.com/drosboro)
* **Douglas Eleutério** - *Convert pdf from S3* - [Lett Digital](https://github.com/orgs/lettdigital)

## License

This project is licensed under the GNU License - see the [LICENSE](LICENSE) file for details
