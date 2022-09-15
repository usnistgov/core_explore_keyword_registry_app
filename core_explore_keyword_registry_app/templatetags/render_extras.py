""" Render extras
"""

from django import template
from django.template import Template, Variable, TemplateSyntaxError

register = template.Library()


class RenderAsTemplateNode(template.Node):
    """Render As Template Node"""

    def __init__(self, item_to_be_rendered):
        self.item_to_be_rendered = Variable(item_to_be_rendered)

    def render(self, context):
        try:
            actual_item = self.item_to_be_rendered.resolve(context)
            return Template(actual_item).render(context)
        except template.VariableDoesNotExist:
            return ""


@register.tag(name="render_as_template")
def render_as_template(parser, args):
    """render as template
    Args:
        parser:
        args:

    Returns:

    """
    content = args.split_contents()
    if len(content) != 2:
        raise TemplateSyntaxError(
            f"'{content[0]}' takes only one argument"
            " (a variable representing a template to render)"
        )

    return RenderAsTemplateNode(content[1])
