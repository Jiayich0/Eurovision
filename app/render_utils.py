"""
Modulo que contiene funciones auxiliares para renderizar
"""
from flask import request, url_for
from wtforms import SelectMultipleField
from wtforms.widgets import CheckboxInput
from markupsafe import Markup

### Funciones auxilares para el formulario de CrearQuiz

class BootstrapListOptions:
    """
    Widged modificado para agrupar las opciones en listas de n elementos
    """
    def __call__(self, field, **kwargs):
        # Numero de elementos por columna
        n = getattr(field, 'elementos_por_fila', 4)
        html = ['<div class="container-fluid">']

        # Iteramos sobre todos los elementos
        for i, subfield in enumerate(field):
            if i % n == 0:
                html.append('<div class="row my-3">')

            num_cols = 12 // n
            # Renderizamos un elemento
            html.append(f'''
                <div class="col-md-{num_cols}">
                    <div class="form-check">
                        {subfield(class_="form-check-input")}
                        <label class="form-check-label" for="{subfield.id}">
                            {subfield.label.text}
                        </label>
                    </div>
                </div>
            ''')

            # Cerramos el grupo correspondiente
            if i % n == n - 1:
                html.append('</div>')

        # Comprobamos si el ultimo elemento esta cerrado o no
        if not html[-1].strip().endswith('</div>'):
            html.append('</div>')

        html.append('</div>')  # close container-fluid
        return Markup(''.join(html))


class MultiCheckboxField(SelectMultipleField):
    widget = BootstrapListOptions()
    option_widget = CheckboxInput()

    def process_data(self, value):
        """
        Ensures only selected values are saved in the data field.
        If no values are selected, set data to an empty list.
        """
        if value is None:
            self.data = []
        else:
            self.data = value

    def pre_validate(self, form):
        """Override to ensure empty data when no checkboxes are selected."""
        if not self.data:
            self.data = []  # Ensure we don't have any leftover data from unchecked checkboxes
        super().pre_validate(form)


### Funciones auxiliares para renderizar una paginacion desde mongo (no tenemos la de flask)

def render_pagination(page, per_page, total_items, endpoint, **kwargs):
    total_pages = max(1, (total_items + per_page - 1) // per_page)

    if total_pages <= 1:
        return ""

    def page_link(p):
        query_args = dict(request.args)
        query_args.update(kwargs)
        query_args['page'] = p
        return url_for(endpoint, **query_args)

    html = ['<nav aria-label="Page navigation">']
    html.append('<ul class="pagination justify-content-center">')

    # Boton anterior
    prev_disabled = 'disabled' if page <= 1 else ''
    html.append(f'''
        <li class="page-item {prev_disabled}">
            <a class="page-link" href="{page_link(page - 1)}" aria-label="Previous">
                <span aria-hidden="true">&laquo;</span>
            </a>
        </li>
    ''')

    #
    for p in range(1, total_pages + 1):
        active = 'active' if p == page else ''
        html.append(f'''
            <li class="page-item {active}">
                <a class="page-link" href="{page_link(p)}">{p}</a>
            </li>
        ''')

    # Siguiente boton
    next_disabled = 'disabled' if page >= total_pages else ''
    html.append(f'''
        <li class="page-item {next_disabled}">
            <a class="page-link" href="{page_link(page + 1)}" aria-label="Next">
                <span aria-hidden="true">&raquo;</span>
            </a>
        </li>
    ''')

    html.append('</ul></nav>')
    return Markup(''.join(html))
