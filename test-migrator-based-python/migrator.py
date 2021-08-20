import javalang
import ast
import astunparse
import os, sys

curr_dir = os.path.dirname(os.path.abspath(__file__))

integer_type = ['int', 'short', 'long', 'byte']
float_type = ['float', 'double']
data_type = integer_type + float_type + ['char', 'bool', 'String']
binaryOp = {'+': ast.Add(), '-':ast.Sub(), '*': ast.Mult(), '/': ast.Div(), '%':ast.Mod(),'==': ast.Eq(), '!=': ast.NotEq(),
            '&&': ast.And(), '||': ast.Or(), '>': ast.Gt(), '>=': ast.GtE(), '<': ast.Lt(), '<=': ast.LtE(),
            '++': ast.Add(), '--': ast.Add(), '+=': ast.Add(), '-=': ast.Sub(), '*=': ast.Mult(), '\=': ast.Div(), '!':ast.Not()}
cmpop = ['==', '!=', '>', '<', '>=', '<=']
operator = ['+', '-', '*', '/', '%']
boolop = ['&&', '||']
unaryop = ['!']
migrate_method = ['__init__', 'setUpClass', 'beforeTest', 'keyspace', 'currentTable', 'createKeyspace',
                  'createKeyspaceName', 'createTable', 'createTable', 'createTableName', 'schemaChange', 'formatQuery',
                  'formatQuery', 'execute']

migrate_func = ['execute', 'createTable']

#TODO: uniop!!!

def convert_value_type(value):

    if value.isdigit():
        try:
            return int(value)
        except ValueError:
            return float(value)
    elif value == 'true' or value == 'false':
        return bool(value)
    elif (value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'"):
        return value[1:-1]
    elif value == 'null':
        return None
    else:
        return value

class ManuallyMigrateFuncs():
    def __init__(self):
        self.import_nodes = []
        self.name_to_func_nodes = {}
        self.funcs_file = os.path.join(curr_dir, 'manually_migrate_funcs.py')

    def get_python_nodes(self):
        fp = open(self.funcs_file, 'r')
        python_root = ast.parse(fp.read())

        for node in python_root.body:
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                self.import_nodes.append(node)
            if isinstance(node, ast.FunctionDef):
                self.name_to_func_nodes[node.name] = node

class TestMigrator:

    def __init__(self, className):
        # open the java file
        #self.java_file = open("javaTemplate.java", "r")
        self.className = className
        self.target_dir = os.path.join(curr_dir, 'java_files')
        self.java_file_name = os.path.join(self.target_dir, self.className + ".java")
        self.result_dir = os.path.join(curr_dir, 'migrate_result')
        self.python_file = os.path.join(self.result_dir, self.className + '.py')

        self.java_file = open(self.java_file_name, "r")
        #self.java_file = open('javaTemplate.java', 'r')
        self.tree = javalang.parse.parse(self.java_file.read())

        # build an empty python ast
        self.python_root = ast.parse("")
        self.test_method = []
        self.before_method = []
        self.method = []
        self.parent_name = None
        self.parent = None
        if className == "CQLTester":
            self.manually_migrate_funcs = ManuallyMigrateFuncs()
            self.manually_migrate_funcs.get_python_nodes()
        else:
            self.manually_migrate_funcs = None
        self.createdTables = None

    def visit_Module(self):
        #self.visit_Import()
        if self.manually_migrate_funcs != None:
            for node in self.manually_migrate_funcs.import_nodes:
                self.python_root.body.insert(len(self.python_root.body), node)
        self.visit_ClassDeclaration()


    def visit_Import(self):
        for path, compilationUnit in self.tree.filter(javalang.tree.CompilationUnit):
            for node in compilationUnit.imports:
                p = node.path
                fileName = ast.alias(name=p, asname=None)
                importNode = ast.Import(names=[fileName])
                self.python_root.body.insert(len(self.python_root.body), importNode)

    def get_parent(self):
        for class_path, class_node in self.tree.filter(javalang.tree.ClassDeclaration):
            if class_node.extends:
                self.parent_name = class_node.extends.name

    def visit_ClassDeclaration(self):

        # get each class declaration nodes
        for class_path, class_node in self.tree.filter(javalang.tree.ClassDeclaration):
            base = []
            if class_node.extends:
                #import_node = ast.ImportFrom(module=class_node.extends.name, names=[ast.alias(name='*', asname=None)], level=0)
                import_node = ast.Import(names=[ast.alias(name = class_node.extends.name, asname=None)])
                self.python_root.body.insert(len(self.python_root.body), import_node)
                extend_class = class_node.extends.name + "." + class_node.extends.name
                base.append(ast.Name(id=extend_class, ctx='Load'))
            else:
                if class_node.name and class_node.name != 'CQLTester':
                    break
                #self.parent_name = class_node.extends.name
            class_dec_node = ast.ClassDef(name=class_node.name, bases=base, body=[], decorator_list=[], keywords=[])
            currClass, init_method = self.class_initialize(class_node, class_dec_node)
            #currClass.classNode = class_dec_node
            class_dec_node.body.insert(len(class_dec_node.body), init_method)

            for node in class_node.body:
                # get each field declaration nodes
                if isinstance(node, javalang.tree.MethodDeclaration):
                    currClass.currLocalVarList = []
                    method_dec = currClass.visit_MethodDeclaration(node)
                    if len(method_dec.body) == 0:
                        continue
                    self.method.append(method_dec.name)
                    if self.manually_migrate_funcs != None:
                        if method_dec.name in self.manually_migrate_funcs.name_to_func_nodes.keys():
                            func_node = self.manually_migrate_funcs.name_to_func_nodes[method_dec.name]
                            if method_dec.name == 'setUpClass':
                                method_dec = func_node
                            elif len(method_dec.args.args) == len(func_node.args.args):
                                method_dec.body = func_node.body
                                method_dec.args = func_node.args
                            else:
                                continue
                    for annotation in node.annotations:
                        if annotation.name == 'Test':
                            self.test_method.append(node.name)
                        if 'Before' in annotation.name:
                            self.before_method.append(node.name)
                    if self.className == 'CQLTester':
                        if method_dec.name in migrate_method:
                            class_dec_node.body.insert(len(class_dec_node.body), method_dec)
                    else:
                        class_dec_node.body.insert(len(class_dec_node.body), method_dec)
            self.createdTables = currClass.createdTables
            self.python_root.body.insert(len(self.python_root.body), class_dec_node)

        #print(astunparse.unparse(self.python_root))

    def class_initialize(self, class_node, class_dec_node):
        # initialize the class nodec
        currClass = javaClassToPython(class_node.name, True, self.parent)

        args = [ast.arg(arg="self", annotation=None, type_comment=None)]

        init_args = []
        attr_name = ast.Name(id = 'self', ctx = 'Load')

        if self.className=='CQLTester':
            init_node = self.manually_migrate_funcs.name_to_func_nodes['__init__']
            for node in init_node.body:
                init_args.append(node)
                currClass.globalVarList.append(node.targets[0].attr)

        if self.parent_name != None and self.parent_name == 'CQLTester':
            func = ast.Attribute(value=ast.Name(id=self.parent_name, ctx='Load'),
                                 attr=self.parent_name, ctx='Load')
            value = ast.Call(func=func, args=[], keywords=[])
            attr = ast.Attribute(value=attr_name, attr='tester', ctx='Store')
            assign = ast.Assign(targets=[attr], value=value)
            init_args.append(assign)
            currClass.globalVarList.append('tester')

        for node in class_node.body:
            if isinstance(node, javalang.tree.FieldDeclaration):
                for n in node.declarators:
                    if n.initializer:
                        value = currClass.visit_variable(n.initializer, 'Load')
                    else:
                        value = ast.Constant(value=None, kind=None)

                    '''
                    if 'static' in node.modifiers:
                        target = ast.Name(id = n.name, ctx = 'Store')
                        assign = ast.Assign(targets=[target], value = value)
                        class_dec_node.body.insert(len(class_dec_node.body), assign)
                        currClass.currLocalVarList.append(n.name)
                        currClass.staticVarList.append(n.name)
                    else:
                    '''
                    if self.className != 'CQLTester':
                        attr = ast.Attribute(value = attr_name, attr = n.name, ctx = 'Store')
                        assign = ast.Assign(targets=[attr], value = value)
                        init_args.append(assign)
                        currClass.globalVarList.append(n.name)

            if isinstance(node, javalang.tree.MethodDeclaration):
                currClass.methodList.append(node.name)

        if len(init_args) == 0:
            pass_stmt = ast.Pass(args=[])
            init_args.append(pass_stmt)

        init_method_name = "__init__"
        init_method = ast.FunctionDef(name=init_method_name, args=ast.arguments(posonlyargs=[], args=args, vararg=None,
                                                                                kwonlyargs=[], kw_defaults=[],
                                                                                kwarg=None,
                                                                                defaults=[]), body=init_args,
                                      decorator_list=[], )

        return currClass, init_method

    def unparse_and_print(self):
        print(astunparse.unparse(self.python_root))
        '''
        for c in self.python_root.body:
            if isinstance(c, ast.ClassDef):
                for node in c.body:
                    if isinstance(node, ast.FunctionDef):
                        for n in node.body:
                            if isinstance(n, ast.Assign):
                                tmp = astunparse.unparse(n.value)
                                print("###########")
                                print(tmp)
                            except:
                                print("--------------------")
                                print(tmp)
                                print(node.name)
        '''

    def unparse_and_save_result(self):
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)
        with open(self.python_file, 'w') as out:
            out.write(astunparse.unparse(self.python_root))

    def delete_python_file_if_exist(self):
        if os.path.exists(self.python_file):
            os.remove(self.python_file)

class javaClassToPython:

    def __init__(self, name, is_class, parent = None):
        self.name = name
        self.is_class = is_class
        self.globalVarList = []
        self.methodList = []
        self.currLocalVarList = []
        self.staticVarList = []
        self.parent = parent
        self.createdTables= []
        self.debug = False

    #TODO: LocalVarList = [] append args + localVarDec
    def visit_MethodDeclaration(self, method_dec_node, debug=False):

        self.debug = debug

        args = []

        if self.is_class:
            args.append(ast.arg(arg="self", annotation=None, type_comment=None))

        for node in method_dec_node.parameters:
            self.currLocalVarList.append(node.name)
            arg = ast.arg(arg = node.name, annotation=None, type_comment=None)
            args.append(arg)

        method_name = method_dec_node.name
        decorator_list = []

        #for node in method_dec_node.annotations:
        #    decorator_list.append(ast.Name(id=node.name, ctx='Load'))

        #if 'static' in method_dec_node.modifiers:
        #    decorator_list.append(ast.Name(id = 'staticmethod', ctx = 'Load'))
        method_node = ast.FunctionDef(name = method_name, args=ast.arguments(posonlyargs=[], args=args, vararg=None,
                                                                             kwonlyargs=[], kw_defaults=[], kwarg=None,
                                                                             defaults=[]), body=[], decorator_list=decorator_list)

        for node in method_dec_node.body:
            body_stmt = self.visit_Statement(node)



            for stmt in body_stmt:
                if self.name != 'CQLTester' and isinstance(stmt, ast.Expr):
                    if isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Attribute):
                        if stmt.value.func.attr in migrate_func:
                            method_node.body.insert(len(method_node.body), stmt)
                elif self.name == 'PstmtPersistenceTest':
                    if isinstance(stmt, ast.Call):
                        method_node.body.insert(len(method_node.body), stmt)
                else:
                    '''
                    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Attribute):
                        print(ast.dump(stmt))
                        print(ast.dump(ast.parse("print(query)")))
                        if stmt.value.func.value.id == 'logger':
                            print()
                    '''
                    method_node.body.insert(len(method_node.body), stmt)

        #self.currLocalVarList = []
        return method_node


    #TODO: visit_Statement(self, node, LocalVarList)
    def visit_Statement(self, node):
        stmt = []
        if isinstance(node, javalang.tree.StatementExpression):
            # swtich node.type
            stmt.append(self.visit_StatementExpression(node))
        elif isinstance(node, javalang.tree.LocalVariableDeclaration):
            for n in node.declarators:
                if n.initializer:
                    stmt.append(self.visit_VariableDeclarator(node, n))
                    self.currLocalVarList.append(n.name)
        elif isinstance(node, javalang.tree.IfStatement):
            stmt.append(self.visit_IfStatement(node))
        elif isinstance(node, javalang.tree.BlockStatement):
            stmt.extend(self.visit_BlockStatement(node))
        elif isinstance(node, javalang.tree.MethodInvocation):
            stmt.append(self.visit_MethodInvocation(node))
        elif isinstance(node, javalang.tree.ReturnStatement):
            stmt.append(self.visit_ReturnStatement(node))
        elif isinstance(node, javalang.tree.WhileStatement):
            stmt.append(self.visit_WhileStatement(node))
        elif isinstance(node, javalang.tree.ForStatement):
            stmt.extend(self.visit_ForStatement(node))
        elif isinstance(node, javalang.tree.Assignment):
            stmt.append(self.visit_Assignment(node))
        elif isinstance(node, javalang.tree.MemberReference):
            stmt.append(self.visit_MemberReference(node))
        elif isinstance(node, javalang.tree.Cast):
            stmt.append(self.visit_Cast(node))
        elif isinstance(node, javalang.tree.BreakStatement):
            stmt.append(self.visit_BreakStmt())
        elif isinstance(node, javalang.tree.ContinueStatement):
            stmt.append(self.visit_ContiuneStmt())
        elif isinstance(node, javalang.tree.TryStatement):
            stmt.append(self.visit_TryStatement(node))
        elif isinstance(node, javalang.tree.CatchClause):
            stmt.append(self.visit_CatchClause(node))
        elif isinstance(node, javalang.tree.ThrowStatement):
            pass
        else:
            pass

        return stmt

    def visit_This(self, node, ctx):
        for n in node.selectors:
            if n.member not in self.staticVarList:
                value = ast.Name(id='self', ctx='Load')
                return ast.Attribute(value=value, attr=n.member, ctx=ctx)
            else:
                return ast.Name(id=n.member, ctx=ctx)

    def visit_TernaryExpression(self, node):
        test = self.visit_variable(node.condition)
        body = self.visit_variable(node.if_true)
        orelse = self.visit_variable(node.if_false)
        return ast.IfExp(test=test, body=body, orelse=orelse)

    def visit_TryStatement(self, node):
        #TODO: block?
        body = []
        for n in node.block:
            body.extend(self.visit_Statement(n))
        #for n in node.catches:
        except_stmt = []
        for n in node.catches[0].block:
            except_stmt.extend(self.visit_Statement(n))
        handlers = ast.ExceptHandler(type=None, name=None, body=except_stmt)
        return ast.Try(body=body, handlers=[handlers], orelse=[], finalbody=[])

    def visit_CatchClause(self, node):
        body = self.visit_Statement(node.block)
        return ast.ExceptHandler(type=None, name=node.name, body=body)

    def visit_ContiuneStmt(self):
        return ast.Continue()

    def visit_BreakStmt(self):
        return ast.Break()

    def visit_Cast(self, node):
        func_name = ast.Name(id=node.type.name, ctx='Load')
        if isinstance(node.expression, javalang.tree.MemberReference) or isinstance(node.expression, javalang.tree.MethodInvocation):
            id = node.expression.member
        else:
            id = node.expression.value
        value = ast.Name(id=id, ctx='Load')
        stmt = ast.Call(func = func_name, args = [value], keywords=[])
        return stmt

    def visit_ClassCreator(self, classCreator):

        class_creator = self.handle_special_dataStructure(classCreator)
        if class_creator != None:
            return class_creator

        func = ast.Name(id = classCreator.type.name, ctx = "Load")
        call = ast.Call(func = func, args=[], keywords=[])

        return call


    def handle_special_dataStructure(self, classCreator):
        if classCreator.type.name == 'HashMap':
            return ast.Dict(keys=[], values=[])
        if classCreator.type.name == 'ArrayList':
            return ast.List(elts=[], ctx='Load')


    def visit_ForStatement(self, forStmt):
        for_stmt = []
        for_control = forStmt.control
        outer_local_var_list = self.currLocalVarList.copy() # copy a list
        if isinstance(for_control, javalang.tree.ForControl):
            for n in for_control.init.declarators:
                init = self.visit_VariableDeclarator(for_control.init, n)
                for_stmt.append(init)
                self.currLocalVarList.append(n.name)
            condition = self.visit_variable(for_control.condition)
            body = self.visit_Statement(forStmt.body)
            for u in for_control.update:
                update = self.visit_Statement(u)
                body.append(update)

            while_stmt = ast.While(test = condition, body = body, orelse = [])
            for_stmt.append(while_stmt)

        elif isinstance(for_control, javalang.tree.EnhancedForControl):

            iter = self.visit_MemberReference(for_control.iterable, 'Load')
            for var in for_control.var.declarators:
                target = ast.Name(id = var.name, ctx="Store")
                self.currLocalVarList.append(var.name)

            body = self.visit_Statement(forStmt.body)

            for_stmt.append(ast.For(target = target, iter = iter, body = body, orelse=[], type_comment=None))

        self.currLocalVarList = outer_local_var_list.copy()

        return for_stmt


    def visit_WhileStatement(self, node):

        condition = self.visit_variable(node.condition, "Load")
        body = self.visit_Statement(node.body)
        whileStmt = ast.While(test = condition, body = body, orelse = [])

        return whileStmt


    def visit_ReturnStatement(self, node):
        n = node.expression
        value = self.visit_variable(n, "Load")
        returnStmt = ast.Return(value = value, decorator_list=[], returns=None, type_comment=None)

        return returnStmt

    def visit_MethodInvocation(self, node):
        stmt = self.handle_special_function(node)
        if stmt != None:
            return stmt

        if node.qualifier == 'logger':
            args = []
            for arg in node.arguments:
                args.append(self.visit_variable(arg, 'Load'))
            return ast.Call(func=ast.Name(id='print', ctx=ast.Load()), args=args,
                            keywords=[])

        args = []
        if node.member == 'execute':
            index = 0
            list = []
            for arg in node.arguments:
                if index == 0:
                    args.append(self.visit_variable(arg, 'Load'))
                else:
                    list.append(self.visit_variable(arg, 'Load'))
                index += 1
            args.append(ast.List(elts=list, ctx='Load'))
        else:
            for argument in node.arguments:
                arg = self.visit_variable(argument, "Load")
                args.append(arg)

        attr_value = None
        if node.qualifier == "" and node.member in self.methodList:
            attr_value = ast.Name(id='self', ctx='Load')
        else:
            if node.qualifier == "" and self.parent != None:
                if node.member in self.parent.method:
                    s = ast.Name(id='self', ctx='Load')
                    attr_value = ast.Attribute(value = s, attr='tester', ctx='Load')
            elif node.qualifier != "":
                if node.qualifier in self.currLocalVarList:
                    attr_value = ast.Name(id=node.qualifier, ctx='Load')
                elif node.qualifier in self.globalVarList:
                    s = ast.Name(id='self', ctx='Load')
                    attr_value = ast.Attribute(value=s, attr=node.qualifier, ctx='Load')
                else:
                    attr_value = ast.Name(id=node.qualifier, ctx='Load')

        if attr_value :
            func = ast.Attribute(value = attr_value, attr = node.member, ctx = "Load")
        else:
            func = ast.Name(id = node.member, ctx = "Load")
        call = ast.Call(func = func, args = args, keywords = [])

        return call

    def visit_BlockStatement(self, blcStmt):

        stmt_list = []
        outer_local_var_list = self.currLocalVarList.copy() # copy a list
        for node in blcStmt.statements:
            stmt = self.visit_Statement(node)
            stmt_list.append(stmt)
        self.currLocalVarList = outer_local_var_list.copy()

        return stmt_list


    def visit_IfStatement(self, node):
        condition = self.visit_variable(node.condition, "Load")
        orelse = []
        if node.else_statement != None:
            orelse.extend(self.visit_Statement(node.else_statement))
        body = self.visit_Statement(node.then_statement)

        ifStmt = ast.If(test = condition, body = [body], orelse = orelse, decorator_list=[], returns=None, type_comment=None)

        return ifStmt


    def visit_StatementExpression(self, stmtExpr):
        node = stmtExpr.expression

        if isinstance(node, javalang.tree.Assignment):
            return self.visit_Assignment(node)

        if isinstance(node, javalang.tree.MethodInvocation):
            value = self.visit_MethodInvocation(node)
            return ast.Expr(value = value)

        if isinstance(node, javalang.tree.MemberReference):
            return self.visit_MemberReference(node)


    def visit_Assignment(self, node):
        if node.type == "=":
            target = self.visit_variable(node.expressionl, "Store")
            value = self.visit_variable(node.value, "Load")

        elif node.type in binaryOp:
            op = binaryOp[node.type]
            target = self.visit_variable(node.expressionl, "Store")
            left = self.visit_variable(node.expressionl, 'Load')
            value = ast.BinOp(left=left, op=op, right=ast.Constant(value=node.value.value, kind=None))

        stmt = ast.Assign(targets=[target], value=value)
        return stmt


    def visit_VariableDeclarator(self, filed_node, node):

        #if isinstance(node, javalang.tree.VariableDeclarator):
        #if filed_node.type.name in data_type:

        if node.initializer == None:
            return None
        elif isinstance(node.initializer, javalang.tree.ArrayInitializer):
            var_list = []
            for node_initializer in node.initializer.initializers:
                var = self.visit_variable(node_initializer, filed_node.type.name)
                var_list.append(var)
            value = ast.List(elts=var_list, ctx='Load')
        else:
            value = self.visit_variable(node.initializer)\

        name = ast.Name(id=node.name, ctx="Store")
        assign = ast.Assign(targets=[name], value=value, type_comment=None)

        return assign


    def visit_BinaryOperation(self, node, ctx = None):

        left = self.visit_variable(node.operandl, ctx)
        right = self.visit_variable(node.operandr, ctx)
        if node.operator in binaryOp:
            op = binaryOp[node.operator]
            if node.operator in cmpop:
                value = ast.Compare(left = left, ops = [op], comparators=[right])
            elif node.operator in operator:
                value = ast.BinOp(left=left, op=op, right=right)
            elif node.operator in boolop:
                value = ast.BoolOp(op = op, values=[left,right])
            else:
                pass
            return value
        elif node.operator == 'instanceof':
            func = ast.Name(id='isinstance', ctx='Load')
            args = [left, right]
            return ast.Call(func=func, args=args, keywords=[])


    def visit_variable(self, node, ctx = None):
        if isinstance(node, javalang.tree.MemberReference):
            return self.visit_MemberReference(node, ctx)  #TODO: i = i + 1
        elif isinstance(node, javalang.tree.BinaryOperation):
            return self.visit_BinaryOperation(node, ctx)
        elif isinstance(node, javalang.tree.MethodInvocation):
            return self.visit_MethodInvocation(node)
        elif isinstance(node, javalang.tree.Literal):
            return self.visit_Literal(node)
        elif isinstance(node, javalang.tree.ClassCreator):
            return self.visit_ClassCreator(node)
        elif isinstance(node, javalang.tree.ArrayCreator):
            return self.visit_ArrayCreator(node)
        elif isinstance(node, javalang.tree.Cast):
            return self.visit_Cast(node)
        elif isinstance(node, javalang.tree.TernaryExpression):
            return self.visit_TernaryExpression(node)
        elif isinstance(node, javalang.tree.This):
            return self.visit_This(node, ctx)
        elif isinstance(node, javalang.tree.ReferenceType):
            return self.visit_ReferenceType(node)
        elif isinstance(node, javalang.tree.Assignment):
            return self.visit_Assignment(node)
        #elif isinstance(node, javalang.tree.NoneType):
        #    print('None!!!')
        elif isinstance(node, javalang.tree.BasicType):
            return self.visit_BasicType(node)
        else:
            return ast.Constant(value=None, kind=None)

    def visit_ReferenceType(self, node):
        return ast.Name(id = node.name, ctx='Load')

    def visit_BasicType(self, node):
        return ast.Name(id = node.name, ctx='Load')

    def visit_ArrayCreator(self, node):
        return ast.List(elts=[], ctx='Load')

    def visit_MemberReference(self, node, ctx = "Load"):
        #Subscript(value=Name(id='b', ctx=Load()), slice=Index(value=Name(id='j', ctx=Load())), ctx=Load())
        if node.selectors:
            for n in node.selectors:
                if isinstance(n, javalang.tree.ArraySelector):
                    value = ast.Name(id=node.member, ctx='Load')
                    if isinstance(n.index, javalang.tree.MemberReference) and n.index.postfix_operators:
                        slice = ast.Index(value=ast.Name(id=n.index.member, ctx='Load'))
                        return ast.Subscript(value=value, slice=slice, ctx='Load')#, self.visit_variable(n.index)
                    else:
                        slice = ast.Index(value = self.visit_variable(n.index))
                        return ast.Subscript(value=value, slice=slice, ctx='Load')

        if len(node.prefix_operators) == 0 and len(node.postfix_operators) == 0:
            return self.visit_get_member(node, ctx)
        else:
            # Assign(targets=[Name(id='i', ctx=Store())], value=BinOp(left=Name(id='i', ctx=Load()), op=Add(), right=Constant(value=1, kind=None)), type_comment=None)
            if len(node.prefix_operators) != 0:
                op = node.prefix_operators[0]
            else:
                op = node.postfix_operators[0]

            if op == '++' or op == '--':
                op = binaryOp[op]

                target = self.visit_get_member(node, 'Store')
                left = self.visit_get_member(node, 'Load')
                return ast.Assign(targets=[target], value = ast.BinOp(left = left, op = op, right = ast.Constant(value=1, kind = None)), type_comment=None)
            elif op == '!':
                return ast.UnaryOp(op=binaryOp['!'], operand=ast.Name(id=node.member, ctx='Load'))


    def visit_get_member(self, node, ctx):
        if node.qualifier == "" and node.member not in self.currLocalVarList:

            if node.member in self.globalVarList:
                value = ast.Name(id='self', ctx='Load')
            elif self.parent != None:
                if node.member in self.parent.globalVarList:
                    value = ast.Attribute(value = ast.Name(id='self', ctx='Load'), attr='tester', ctx=ctx)
            else:
                return ast.Name(id=node.member, ctx=ctx)

            return ast.Attribute(value=value, attr=node.member, ctx=ctx)
        return ast.Name(id=node.member, ctx=ctx)

    def visit_Literal(self, node):

        var_value = node.value
        value = ast.Constant(value = convert_value_type(var_value), kind=None)

        return value

    def handle_special_function(self, node):
        #String.format

        attr_value = None
        if node.qualifier == "" and node.member in self.methodList:
            attr_value = ast.Name(id='self', ctx='Load')
        else:
            if node.qualifier == "" and self.parent != None:
                if node.member in self.parent.method:
                    s = ast.Name(id='self', ctx='Load')
                    attr_value = ast.Attribute(value=s, attr='tester', ctx='Load')
            elif node.qualifier != "":
                if node.qualifier in self.currLocalVarList:
                    attr_value = ast.Name(id=node.qualifier, ctx='Load')
                elif node.qualifier in self.globalVarList:
                    s = ast.Name(id='self', ctx='Load')
                    attr_value = ast.Attribute(value=s, attr=node.qualifier, ctx='Load')
                else:
                    attr_value = ast.Name(id=node.qualifier, ctx='Load')

        if node.member == 'format' and node.qualifier=='String':
            values = []
            for arg in node.arguments:
                value = self.visit_variable(arg, 'Load')
                values.append(value)

            if len(values) > 2:
                right = ast.Tuple(elts = values[1:], ctx='Load')
            else:
                right = values[1]

            stmt= ast.BinOp(left=values[0], op=ast.Mod(), right = right)
            return stmt

        if node.member == 'size':
            func = ast.Name(id='len', ctx='Load')
            args = [attr_value]
            return ast.Call(func=func, args=args, keywords=[])

        if node.member == 'contains':
            left = self.visit_variable(node.arguments[0], 'Load')
            comparators = [attr_value]
            op = [ast.In()]
            return ast.Compare(left=left, ops = op, comparators = comparators)

        if node.member == 'get' and len(node.arguments) != 0:
            value = attr_value
            slice = ast.Index(value = self.visit_variable(node.arguments[0]))
            return ast.Subscript(value=value, slice=slice, ctx='Load')

        if node.member == 'add':
            func = ast.Attribute(value = attr_value, attr='append', ctx='Load')
            args = [self.visit_variable(node.arguments[0])]
            return ast.Call(func=func, args=args, keywords=[])

        if node.member == 'isEmpty':
            return ast.UnaryOp(op=ast.Not(), operand=attr_value)


def migrate_single_test(testMigrator):
    testMigrator.delete_python_file_if_exist()
    testMigrator.visit_Module()
    testMigrator.unparse_and_save_result()
    #testMigrator.unparse_and_print()

    return testMigrator

def get_migrator(fileName):
    testMigrator = TestMigrator(fileName)
    testMigrator.get_parent()
    return testMigrator

def migrate_multiple_tests(fileNames):
    testMigrators = {}
    for fileName in fileNames:
        testMigrator = get_migrator(fileName)
        testMigrators[testMigrator.className] = testMigrator

    pending_migrator = list(testMigrators.keys())

    for testMigrator_name in testMigrators.keys():
        if testMigrator_name in pending_migrator:
            testMigrator = testMigrators[testMigrator_name]
            if testMigrator.parent_name != None and testMigrator.parent_name in pending_migrator:
                testMigrator.parent = testMigrators[testMigrator.parent_name]
                migrate_single_test(testMigrator.parent)
                pending_migrator.remove(testMigrator.parent_name)
            elif testMigrator.parent_name != None and testMigrator.parent_name not in pending_migrator:
                testMigrator.parent = testMigrators[testMigrator.parent_name]
            migrate_single_test(testMigrator)
            pending_migrator.remove(testMigrator.className)

    return testMigrators.values()

def migrate_all_tests():
    path = os.path.join(curr_dir, 'java_files')
    files = os.listdir(path)

    fileNames = []

    for file in files:
        if not os.path.isdir(file) and file.find(".java") != -1:
            fileNames.append(file[:-5])

    return migrate_multiple_tests(fileNames)

if __name__ == '__main__':

    #migrate_all_tests()

    migrate_single_test('CQLTester')


    #testMigrator.unparse_and_save_result()
    #print(astunparse.unparser(testMigrator.python_root))





