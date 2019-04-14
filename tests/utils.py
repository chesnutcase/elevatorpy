# given a list of statements and captued stdout list, check that statements in the list appear in order
def check_stdout(statements, outputs):
    indexes = []
    for statement in statements:
        try:
            id = outputs.index(statement)
        except ValueError:
            raise ValueError("{} not found in stdout: {}".format(statement, outputs))
        indexes.append(id)
    if sorted(indexes) != indexes:
        raise ValueError("statements present but not in order: \nstatements: \n{}\n output: \n{}\n".format(statements, outputs))
    return True
