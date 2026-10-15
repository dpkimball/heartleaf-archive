# Heartleaf — historical archive

Django web interface and USDA/FDA ingestion tools.

A personal receipt and food-information project developed in 2017–2019. Heartleaf supplied the web interface and data ingestion; TwinPeaks supplied the Java backend; Monadnock explored Android access. These repositories preserve that work as historical source, with publication cleanup performed in 2026. They are not maintained or presented as production-ready software.

## Related repositories

[Heartleaf](https://github.com/dpkimball/heartleaf-archive) · [Twinpeaks](https://github.com/dpkimball/twinpeaks-archive) · [Monadnock](https://github.com/dpkimball/monadnock-archive)

## Publication changes

The original third-party theme, scripts, fonts, artwork, and template markup were replaced with a small original interface. Database exports, credentials, cached FDA HTML, and desktop screenshots were removed. Configuration examples are provided; copy them locally and supply your own values. The historical dependency versions and external data formats have not been modernized.

## Historical environment

The historical stack targeted Python 3.6 / Django 2.1.5 and a separate TwinPeaks instance. Review `requirements.txt`, `local.env.example`, and `oxbow_docker.env.example`. Supply PostgreSQL and the required environment variables locally. The Compose file is historical and includes machine-specific/backend-image references. The old cached FDA HTML is omitted, so offline scraping is unavailable.

## Limitations

No automated end-to-end suite is provided. OCR code is an unfinished historical experiment. Receipt scores were placeholders, not validated health advice. The replacement web templates have been checked independently of a running Django/backend stack.

## License and attribution

Original contributions and publication replacements are MIT licensed under LICENSE. Third-party portions retain their own notices and terms; see THIRD_PARTY.md. No ownership of upstream sample code is claimed.
