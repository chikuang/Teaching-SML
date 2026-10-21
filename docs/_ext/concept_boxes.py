"""Render semantic learning boxes consistently in the web book and PDF."""
from html import escape
from docutils import nodes
from sphinx import addnodes
from sphinx.transforms import SphinxTransform


class concept_box(nodes.Admonition, nodes.Element):
    pass


class ConceptBoxes(SphinxTransform):
    default_priority = 500

    def apply(self):
        for node in list(self.document.findall(nodes.admonition)):
            kinds = [k for k in ("core", "method", "boundary")
                     if f"course-{k}" in node.get("classes", [])]
            if not kinds:
                continue
            box = concept_box("", kind=kinds[0], ids=node.get("ids", []))
            box["title"] = node[0].astext()
            for child in list(node.children[1:]):
                box += child
            node.replace_self(box)


class LatexCourseOverview(SphinxTransform):
    """Keep the web introduction as one PDF chapter before the course chapters."""
    default_priority = 600

    def apply(self):
        if self.app.builder.format != "latex" or self.env.docname != "index":
            return
        root = next(self.document.findall(nodes.section))
        trees = list(root.findall(addnodes.toctree))
        for tree in trees:
            tree.parent.remove(tree)
        overview = nodes.section(ids=["course-overview"])
        overview += nodes.title("", "Course overview")
        for child in list(root.children[1:]):
            root.remove(child)
            overview += child
        root += overview
        for tree in trees:
            root += tree


def visit_html(self, node):
    self.body.append(self.starttag(node, "aside", CLASS=f"admonition course-{node['kind']}"))
    self.body.append(f'<p class="admonition-title">{escape(node["title"])}</p>')


def depart_html(self, node):
    self.body.append("</aside>\n")


def visit_latex(self, node):
    self.body.append("\n\\begin{coursebox}{%s}{%s}\n" %
                     (node["kind"], self.encode(node["title"])))


def depart_latex(self, node):
    self.body.append("\n\\end{coursebox}\n")


def setup(app):
    app.add_node(concept_box, html=(visit_html, depart_html),
                 latex=(visit_latex, depart_latex))
    app.add_transform(ConceptBoxes)
    app.add_transform(LatexCourseOverview)
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}
