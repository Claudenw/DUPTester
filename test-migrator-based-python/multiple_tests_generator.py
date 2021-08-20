import javalang
import ast
import astunparse
import os, sys
import migrator

curr_dir = os.path.dirname(os.path.abspath(__file__))
base_file = os.path.join(curr_dir, "base_file.py")

def get_file_name(className, testName):
    return  "unitTest_cass_" + className + "_" + testName + "_upgrade_test.py"

def get_class_name(testName):
    return "cass"  + testName + "UpgradeTest"

def get_test_name(className, testName):
    return className + "_" + testName

def parse_based_file():
    fp = open(base_file, "r")

    # build an python ast for base file
    return ast.parse(fp.read())


def handle_parent_class(testMigrator):
    body = []
    if testMigrator.parent != None:
        attr_name = ast.Name(id='test', ctx='Load')
        attr = ast.Attribute(value=attr_name, attr='tester', ctx='Store')

        func_required = testMigrator.parent.before_method
        for func in func_required:
            args = []
            if func == 'setUpClass':
                args.append(ast.Name(id='num_nodes', ctx='Load'))
                args.append(ast.Name(id='subnet', ctx='Load'))

            func_node = ast.Attribute(value=attr, attr=func, ctx='Load')
            call = ast.Call(func=func_node, args=args, keywords=[])
            expr = ast.Expr(value=call)
            body.append(expr)

    return body

def build_test_old_version_node(testMigrator, funcDef_node, test_old_version_node):


    args =  [ast.arg(arg="self", annotation=None, type_comment=None)]


    body = []

    class_node = ast.Name(id='test', ctx='Store')

    func = ast.Attribute(value = ast.Name(id=testMigrator.className, ctx='Load'), attr=testMigrator.className, ctx='Load')
    value = ast.Call(func=func, args=[], keywords=[])
    assign = ast.Assign(targets=[class_node], value = value, type_comment=None)
    body.append(assign)

    body.extend(handle_parent_class(testMigrator))
    func_required = []
    func_required.extend(testMigrator.before_method)
    func_required.append(funcDef_node.name)


    for func in func_required:
        func_node = ast.Attribute(value = class_node, attr=func, ctx='Load')
        call = ast.Call(func = func_node,args=[], keywords=[])
        expr = ast.Expr(value=call)

        body.append(expr)

    test_old_version_node.args = args


    tables = test_old_version_node.body[-1]
    test_old_version_node.body = test_old_version_node.body[:-1]
    test_old_version_node.body.extend(body)

    if testMigrator.parent_name != None and testMigrator.parent_name == 'CQLTester':
        test_old_version_node.body.append(tables)


    return test_old_version_node


def build_test_new_version_node(testMigrator, funcDef_node, test_new_version_node, test_old_version_node):
    '''
    index = 0
    for node in test_old_version_node.body:
        index += 1
        #print(ast.dump(node))
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func.value, ast.Name):
            print(ast.dump(node))
            break
    body = test_old_version_node.body[:index-1]
    '''
    body = test_old_version_node.body[:-2]
    body.extend(test_new_version_node.body)
    test_new_version_node.body = body


def generate_test(testMigrator, funcDef_node, test_id):
    python_root = parse_based_file()

    for node in python_root.body:
        if isinstance(node, ast.ClassDef):
            for n in node.body:
                if isinstance(n, ast.FunctionDef):
                    if n.name == 'test_old_version':
                        test_old_version_node = build_test_old_version_node(testMigrator, funcDef_node, n)


    for node in python_root.body:
        if isinstance(node, ast.ClassDef):
            for n in node.body:
                if isinstance(n, ast.FunctionDef):
                    if n.name == 'test_new_version':
                        build_test_new_version_node(testMigrator, funcDef_node, n, test_old_version_node)

    index = 0
    for node in python_root.body:
        index += 1
        if isinstance(node, ast.ClassDef):
            class_index = index-1
            test_name_node = ast.Assign(targets=[ast.Name(id='testName', ctx='Store')], value=ast.Constant(value=get_test_name(testMigrator.className, funcDef_node.name), kind=None), type_comment=None)
            test_id_node = ast.Assign(targets=[ast.Name(id='testId', ctx='Store')], value=ast.Constant(value=test_id, kind=None), type_comment=None)

            node.name = get_class_name(funcDef_node.name)
            #node.body.insert(len(node.body), test_old_version_node)
        if isinstance(node, ast.If):
            if node.test.left.id == '__name__':
                for n in node.body:
                    if isinstance(n, ast.Assign):
                        if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name):
                            if n.value.func.id == 'testClassName':
                                n.value.func.id = get_class_name(funcDef_node.name)


    python_root.body.insert(class_index, test_name_node)
    python_root.body.insert(class_index, test_id_node)
    import_node = ast.Import(names=[ast.alias(name=testMigrator.className, asname=None)])
    python_root.body.insert(class_index, import_node)
    if testMigrator.parent != None:
        import_node = ast.Import(names=[ast.alias(name=testMigrator.parent_name, asname=None)])
        python_root.body.insert(class_index, import_node)


    #filePath = os.path.join(curr_dir, "..", "src", "cass", "generated_files")
    filePath = os.path.join(curr_dir, "generated_files")
    fileName = os.path.join(filePath, get_file_name(testMigrator.className, funcDef_node.name))

    if not os.path.exists(filePath):
        os.makedirs(filePath)
    with open(fileName, 'w') as out:
        out.write(astunparse.unparse(python_root))


def traverse_single_migrated_file(testMigrator, test_id):

    for class_node in testMigrator.python_root.body:
        if isinstance(class_node, ast.ClassDef):
            for node in class_node.body:
                if isinstance(node, ast.FunctionDef) and node.name in testMigrator.test_method:
                    generate_test(testMigrator, node, test_id)
                    test_id += 1

    return test_id

def traverse_all_migrated_files():
    testMigrators = migrator.migrate_all_tests()
    test_id = 0
    for testMigrator in testMigrators:
        test_id = traverse_single_migrated_file(testMigrator, test_id)
        test_id += 1

if __name__ == '__main__':

    #traverse migrated files
    traverse_all_migrated_files()


