from fastapi.templating import Jinja2Templates

env = Jinja2Templates(directory="app/templates")

TemplateResponse = env.TemplateResponse

def render(path, *args, **kwargs):
    template = env.get_template(path)
    return template.render(*args, **kwargs)
