"""
Test CSS Requirements.
"""
from bs4 import BeautifulSoup
import pytest
import file_clerk.clerk as clerk
from webcode_tk import contrast_tools as contrast
from webcode_tk import css_tools as css
from webcode_tk import html_tools as html

project_path = "project/"
html_files = html.get_all_html_files(project_path)
styles_by_html_files = css.get_styles_by_html_files(project_path)
color_contrast_results = []
color_contrast_results = css.get_project_color_contrast_report(project_path)
no_style_attribute_tests = []
REQUIRED_ELEMENTS = (
    "header",
    "nav",
    "article or section",
    "footer",
)
required_properties = {
    "header": {"properties": ("padding",),},
    "nav": {"properties": ("padding",),},
    "article": {"properties": ("padding",),},
    "aside": {"properties": ("padding",),},
    "hgroup": {"properties": ("padding",),},
    "section": {"properties": ("padding",),},
    "footer": {"properties": ("padding",),},
}
ILLEGAL_FONTS = ("comic sans ms", "comic sans", "times new roman")

def set_style_attribute_tests(path):
    results = []
    for file in html_files:
        filename = clerk.get_file_name(file)
        html = clerk.file_to_string(file)
        soup = BeautifulSoup(html, "html.parser")
        tags_with_style = soup.find_all(lambda tag: tag.has_attr('style'))
        number = len(tags_with_style)
        result = ""
        expected = f"pass: in {filename}, there are no tags with a style attribute."
        if number > 0:
            result = f"fail: in {filename}, there are {number} tags with a style attribute applied."
        else:
            result = expected
        results.append((result, expected))
    return results


def get_unique_font_families(project_folder):
    font_rules = css.get_unique_font_rules(project_folder)
    font_families_tests = []
    illegal_font_usage = False
    illegal_fonts = set()
    for file in font_rules:
        # apply the file, unique rules, unique selectors, and unique values
        filename = file.get("file")
        filename = clerk.get_file_name(filename)
        unique_rules = file.get("rules")
        unique_values = set()
        for rule in unique_rules:
            value = rule.get("family")
            font_stack = value.split(",")
            first_font = font_stack[0].lower()
            first_font = first_font.replace("'", "")
            if first_font in ILLEGAL_FONTS:
                illegal_fonts.add(font_stack[0])
            illegal_font_usage = bool(illegal_fonts)
            unique_values.add(tuple(font_stack))
        passes_values = len(unique_values) > 0 and len(unique_values) <= 2
        
        message = ""
        expected_number = len(unique_values)
        expected = f"pass: {filename} has 2 fonts."
        if expected_number > 2:
            expected_number = 2
            expected = f"pass: {filename} has {expected_number} fonts."
        elif expected_number < 1:
            expected_number = 1
            expected = f"pass: {filename} has {expected_number} font."
        if passes_values:
            if not illegal_font_usage:
                if len(unique_values) == 1:
                    expected = f"pass: {filename} has 1 font."
                message = expected
            else:
                message = f"fail: {filename} applies "
                for font in illegal_fonts:
                    if len(illegal_fonts) > 1:
                        message += font + " and "
                    else:
                        message += font
                message += " - select a different font."
        else:
            message = f"fail: {filename}"
            if len(unique_values) > 2:
                message += " has too many fonts (more than 2)."
            else:
                message += " has no font family applied."
        font_families_tests.append((expected, message))
    return font_families_tests


def get_font_rules_data(font_tests):
    rules_data = []
    for test in font_tests:
        rules_data.append(test[:2])
    return rules_data


def get_font_selector_data(font_tests):
    rules_data = []
    for test in font_tests:
        rules_data.append((test[0], test[2]))
    return rules_data


def get_html_elements_required_and_used(project_path, required_properties):
    required_and_used = set()

    # get required elements (regardless of whether they are present or not)
    for element in required_properties.keys():
        if element in REQUIRED_ELEMENTS:
            required_and_used.add(element)

    # add any elements present in the required properties
    for file in html_files:
        for element in required_properties.keys():
            if "or" in element:
                options = [opt.strip() for opt in element.split("or")]
                for element in options:
                    number = html.get_num_elements_in_file(element, file)
                    if number:
                        required_and_used.add(element)
            number = html.get_num_elements_in_file(element, file)
            if number:
                required_and_used.add(element)
    return required_and_used


def prep_properties_applied_report(project_path, required_properties,
                                   required_and_used):
    # Figure out how to only test for required and used elements
    properties_applied_report = css.get_properties_applied_report(
        project_path,
        required_properties
    )
    final_report = set()
    # get all elements from required_and_used
    html_files = html.get_all_html_files(project_path)
    actual_elements = set()
    for file in html_files:
        for element in required_and_used:
            element = html.get_elements(element, file)
            if element:
                element_name = element[0].name
                actual_elements.add(element_name)
    for actual_element in actual_elements:
        for error in properties_applied_report:
            if actual_element in error:
                final_report.add(error)
    return final_report


def get_required_properties(required_properties, has_required_properties,
                            styles_by_files):
    for file in styles_by_files:
        declarations = file.get("stylesheets")
        for declaration in declarations:
            prop = declaration.property
            if prop in required_properties:
                has_required_properties[prop] = True
            elif "background" in prop:
                # using shorthand?
                split_values = declaration.value.split()
                for value in split_values:
                    if css.color_tools.is_hex(value):
                        has_required_properties["background-color"] = True


def applies_css(styles_by_html_files: list) -> list:
    results = []
    for item in styles_by_html_files:
        path = item.get("file")
        filename = clerk.get_file_name(path)
        expected = f"pass: {filename} applies CSS."
        sheets = item.get("stylesheets")
        applies_styles = False
        if sheets:
            for sheet in sheets:
                if sheet.text:
                    applies_styles = True
        if applies_styles:
            result = expected
        else:
            result = f"fail: {filename} does not apply CSS"
        results.append((result, expected))
    return results


required_and_set = get_html_elements_required_and_used(project_path, required_properties)
font_families_tests = get_unique_font_families(project_path)
style_attributes_data = set_style_attribute_tests(html_files)
stylesheets = css.get_all_project_stylesheets(project_path)
required_properties = prep_properties_applied_report(project_path,
                                                     required_properties,
                                                     required_and_set)
applies_styles = applies_css(styles_by_html_files)


@pytest.fixture
def project_folder():
    return project_path


@pytest.fixture
def html_styles():
    return styles_by_html_files


@pytest.fixture
def html_docs():
    return html_files


@pytest.mark.parametrize("result,expected", applies_styles)
def test_for_any_css_tag_or_stylesheet(result, expected):
    assert result == expected


@pytest.mark.parametrize("result,expected", style_attributes_data)
def test_files_for_style_attribute_data(result, expected):
    assert result == expected


@pytest.mark.parametrize("message",
                         color_contrast_results)
def test_files_for_contrast_results(message):
    assert "pass: " in message[:6]


@pytest.mark.parametrize("expected,result", font_families_tests)
def test_files_for_2_font_families_max(expected, result):
    assert result == expected


@pytest.mark.parametrize("message", required_properties)
def test_for_required_properties(message):
    assert "pass:" in message[:6]


@pytest.fixture
def styles_by_files():
    return styles_by_html_files


def test_for_breakpoints(styles_by_files):
    # at least one break point per file
    expected_num = len(styles_by_files)
    breakpoints = 0
    for styles in styles_by_files:
        for stylesheet in styles.get("stylesheets"):
            at_rules = css.get_all_at_rules(stylesheet)
            if at_rules:
                for at_rule in at_rules:
                    rule = at_rule[1].get("at_rule")
                    if "@media screen" in rule:
                        breakpoints += 1
    assert expected_num >= breakpoints
