from pathlib import Path
import re


from sqlalchemy.util.tool_support import code_writer_cmd

sa_path = Path(__file__).parent.parent / "lib/sqlalchemy"


section_re = re.compile(
    r"^# START GENERATED CYTHON IMPORT$\n(.*)\n"
    r"^# END GENERATED CYTHON IMPORT$",
    re.MULTILINE | re.DOTALL,
)
# start = re.compile("^# START GENERATED CYTHON IMPORT$")
# end = re.compile("^# END GENERATED CYTHON IMPORT$")
code = '''\
# START GENERATED CYTHON IMPORT
# This section is automatically generated by the script tools/cython_imports.py
try:
    # NOTE: the cython compiler needs this "import cython" in the file, it
    # can't be only "from sqlalchemy.util import cython" with the fallback
    # in that module
    import cython
except ModuleNotFoundError:
    from sqlalchemy.util import cython


def _is_compiled() -> bool:
    """Utility function to indicate if this module is compiled or not."""
    return cython.compiled  # type: ignore[no-any-return]


# END GENERATED CYTHON IMPORT\
'''


def run_file(cmd: code_writer_cmd, file: Path):
    content = file.read_text("utf-8")
    count = 0

    def repl_fn(match):
        nonlocal count
        count += 1
        return code

    content = section_re.sub(repl_fn, content)
    if count == 0:
        raise ValueError(
            "Expected to find comment '# START GENERATED CYTHON IMPORT' "
            f"in cython file {file}, but none found"
        )
    if count > 1:
        raise ValueError(
            "Expected to find a single comment '# START GENERATED CYTHON "
            f"IMPORT' in cython file {file}, but {count} found"
        )
    cmd.write_output_file_from_text(content, file)


def run(cmd: code_writer_cmd):
    i = 0
    for file in sa_path.glob(f"**/*_cy.py"):
        run_file(cmd, file)
        i += 1
    cmd.write_status(f"\nDone. Processed {i} files.")


if __name__ == "__main__":
    cmd = code_writer_cmd(__file__)

    with cmd.run_program():
        run(cmd)