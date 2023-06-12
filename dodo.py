import glob


def task_gitclean():
    """Clean all generates"""
    return {'actions': ['git clean -fdx'], }


def task_test():
    """Run tests"""
    return {'actions': ['python3 -m unittest -v'], }


def task_codestyle():
    """Check codestyle with flake8"""
    return {'actions': ['flake8 source']}


def task_docstyle():
    """Check documentation with pydocstyle"""
    return {'actions': ['pydocstyle source']}


def task_pot():
    """Make .pod pattern"""
    return {'actions': ['pybabel extract -o locales/template.pot source'],
            'targets': ['locales/template.pot'], }


def task_po():
    """Update translation"""
    return {'actions': ['pybabel update -D converty -i locales/template.pot -d locales'],
            'file_dep': ['locales/template.pot'],
            'targets': glob.glob("locales/*/LC_MESSAGES/converty.po"), }


def task_mo():
    """Compile translation"""
    return {'actions': ['pybabel compile -D converty -d locales'],
            'file_dep': glob.glob("locales/*/LC_MESSAGES/converty.po"),
            'targets': glob.glob("locales/*/LC_MESSAGES/converty.mo"), }


def task_docs():
    """Make html documantation"""
    return {'actions': ['sphinx-build docs _build'],
            'file_dep': glob.glob("source/*.py"),
            'task_dep': ['mo']
}
