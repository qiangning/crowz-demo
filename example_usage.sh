#!/bin/bash
python cli.py create-instruction instruction-demo example_project/example_instruction.md
python cli.py create-tutorial example_project/example_tutorial.json
python cli.py create-exam example_project/example_exam.json
python cli.py prepare-exam example_project/example_batch.json
# python cli.py launch-exam example_project/example_batch.json
# python cli.py list-instructions
# python cli.py list-tutorials
# python cli.py expire-hit-group 3UHBSK1L5NRDWP557UGKO8OD1QKUOP
# python cli.py get-exam-report exam-demo
# python cli.py get-exam-batch-result exam-batch-demo