"""
Test for HTML requirements
"""
import pytest
import file_clerk.clerk as clerk
from webcode_tk import html_tools as html

project_dir = "project/"
all_html_files = html.get_all_html_files(project_dir)

# List of required elements (per web page)
required_elements = [("doctype", 1),
                     ("html", 1),
                     ("head", 1),
                     ("title", 1),
                     ("h1", 1),
                     ("main", 1)]

min_required_elements = [
    ("figure", 2),
    ("header", 1),
    ("footer", 1),
    ("p", 4),
    ("div or section or article", 2),
    ("img", 2),
    ("a", 4),
    ("figcaption", 2)]

exact_number_of_elements = html.get_number_of_elements_per_file(
    project_dir, required_elements
)
min_number_of_elements = html.get_number_of_elements_per_file(
    project_dir, min_required_elements
)


@pytest.fixture
def html_files():
    html_files = html.get_all_html_files(project_dir)
    return html_files


def test_header_for_h1_tag_inside(html_files):
    expected = len(html_files)
    num_h1s = 0
    for file in html_files:
        headers = html.get_elements("header", file)
        header_contents = html.get_element_content(headers[0])
        num_h1s += header_contents.count("<h1>")
    assert num_h1s == expected


def test_has_index_file(html_files):
    assert "project/index.html" in html_files


@pytest.mark.parametrize("file,element,num", exact_number_of_elements)
def test_files_for_exact_number_of_elements(file, element, num):
    if not html_files:
        assert False
    actual = html.get_num_elements_in_file(element, file)
    assert actual == num


@pytest.mark.parametrize("file,element,num", min_number_of_elements)
def test_files_for_minimum_number_of_elements(file, element, num):
    if not html_files:
        assert False
    if "or" in element.lower():
        elements = element.split()
        actual = 0
        for el in elements:
            el = el.strip()
            actual += html.get_num_elements_in_file(el, file)
    else:
        actual = html.get_num_elements_in_file(element, file)
    assert actual >= num


def test_number_of_html_files():
    image_files = []
    image_files += clerk.get_all_files_of_type(project_dir, "html")
    assert len(image_files) >= 4


def test_number_of_image_files():
    num_html_files = len(clerk.get_all_files_of_type(project_dir, "html"))
    image_files = []
    image_files += clerk.get_all_files_of_type(project_dir, "jpg")
    image_files += clerk.get_all_files_of_type(project_dir, "png")
    image_files += clerk.get_all_files_of_type(project_dir, "gif")
    image_files += clerk.get_all_files_of_type(project_dir, "svg")
    image_files += clerk.get_all_files_of_type(project_dir, "webp")
    expected = num_html_files * 2
    num_image_files = len(image_files)
    assert num_image_files >= expected
