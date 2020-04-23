# Setup aws credentials
`vi ~/.aws/credentials`
You should see things like
```
[default]
aws_access_key_id = ...
aws_secret_access_key = ...
```
Typically if we have multiple aws credentials, we will append to this file other profiles, and it will look like:
```
[default]
aws_access_key_id = ...
aws_secret_access_key = ...
[profile_name_1]
aws_access_key_id = ...
aws_secret_access_key = ...
[profile_name_2]
aws_access_key_id = ...
aws_secret_access_key = ...
```

# Configure this client 
`python cli.py config`
- What's your endpoint url? https://crowd.people.bingo
- What's your username? omitted
- Input your password. omitted
- Which aws session to use? choose one profile that you put in `~/.aws/credentials` 
You can always go to `~/.crowz/config.json` to check or directly modify your configurations. The code above is simply helping you manage `config.json`.

# Login
`python cli.py login`
This will use the username and password you provided in the configuration above

# Usage

## Create instructions
`python cli.py create-instruction [instruction-name] [instruction-markdown-file]`
For instance, 
```
python cli.py create-instruction instruction-demo example_project/example_instruction.md
```
If success, you'll see a url to the instruction you've created. If you receive error message saying that "an old instruction exists" and you want to overwrite it, just add a flag `--overwrite` or `-o` to overwrite it. This overwriting flag exists for other operations below as well.

## Create tutorials
`python cli.py create-tutorial [tutorial-json-file]` For instance,
```
python cli.py create-tutorial example_project/example_tutorial.json
```
Again, you'll see a url to your tutorial, and you can use `-o` to overwrite another tutorial with the same name.

## Create exams
`python cli.py create-exam [exam-json-file]` For instance
```
python cli.py create-exam example_project/example_exam.json
```

## Prepare exams
`python cli.py prepare-exam [exam-batch-json-file]` For instance,
```
python cli.py prepare-exam example_project/example_batch.json
```

## Launch exam on MTurk
For instance,
```
python cli.py launch-exam example_project/example_batch.json
```
It will launch it on MTurk and return you a url to it. Using sandbox or production is determined by corresponding flags in the `example_batch.json` file above.

## Other functions
```
python cli.py list-instructions # list all instructions created by yourself
python cli.py list-tutorials # list all tutorials created by yourself
python cli.py expire-hit-group [group-id] # very handy in testing
```

Below are to get analysis of your exam:
```
python cli.py get-exam-report [exam-name] # check workers' performance on each of your questions in the exam
python cli.py get-exam-batch-result [exam-batch-name] # check workers' performance on each of your questions in the exam batch
```
You can see `example_project/exam_batch_result_exam-batch-demo.json` and `example_project/exam_report_exam-demo.json` to take a look at the type of information it tells you. Basically, it tells you
- for each question, how many people have tried on it and how many people have answered it corrected (this is important because if people rarely get it correct, then this question may be problematic and you may want to disable it)
- for each attempt, who was the worker, what's the score, how long did the worker spend on this question, etc.