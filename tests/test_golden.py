import contextlib
import io
import logging
import os
import tempfile
from pathlib import Path

import pytest

from src import machine
from src.compiler import main as compile


@pytest.mark.golden_test("../golden/*.yml")
def test_machine_with_golden(golden, caplog) -> None:  # noqa: ANN001
    caplog.set_level(logging.INFO)

    with tempfile.TemporaryDirectory() as tmpdirname:
        source = os.path.join(tmpdirname, "source.asm")
        input_stream = os.path.join(tmpdirname, "input.txt")
        target = os.path.join(tmpdirname, "target.bin")

        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["in_source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["in_stdin"])
        
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            compile(Path(source), Path(target))
            print("============================================================")
            machine.main(Path(target), Path(input_stream))
        
        with open(target, 'rb') as file:
            code = file.read()

        assert code == golden.out["out_code"]
        assert stdout.getvalue() == golden.out["out_stdout"]
        assert caplog.text == golden.out["out_log"] 