#!/usr/bin/env vpython3
import logging
import clang
import clang.cindex
from clang.cindex import Diagnostic, CursorKind, TokenKind, TranslationUnit, TypeKind

logger = logging.getLogger(__name__)

clang.cindex.Config.set_library_file('libclang-21.so')

class CTBase(object):
    def __init__(self, namespace):
        self.namespace = "::".join(namespace)+"::" if namespace else ""

    @staticmethod
    def getName(elem):
        field_name = elem.spelling
        if field_name.find('(') > 0:
            field_name = f'unnamed_{elem.hash}'
        return field_name

    @staticmethod
    def ctype2ctypes(t):
        if t.kind == TypeKind.ELABORATED:
            return CTBase.getName(t.get_declaration())
        if t.kind == TypeKind.RECORD:
            return CTBase.getName(t.get_declaration())
        if t.kind == TypeKind.POINTER:
            ti = t.get_pointee().get_canonical()
            if ti.kind == TypeKind.RECORD:
                # struct/union
                return f"POINTER({CTBase.ctype2ctypes(ti)})"
            elif ti.kind == TypeKind.FUNCTIONPROTO:
                #function
                argtypes = []
                argnames = []
                for arg in ti.argument_types():
                    argtypes.append(CTBase.ctype2ctypes(arg))
                    argnames.append(arg.spelling)
                argtypes = ", ".join(argtypes)
                return f"CFUNCTYPE({CTBase.ctype2ctypes(ti.get_result())}, {argtypes})"
            elif ti.kind == TypeKind.FUNCTIONNOPROTO:
                return f"CFUNCTYPE({CTBase.ctype2ctypes(ti.get_result())})"
            # simple type
            return f"POINTER({CTBase.ctype2ctypes(ti)})"
        elif t.kind == TypeKind.CONSTANTARRAY:
            ti = t.get_array_element_type()
            if ti.kind == TypeKind.POINTER:
                tti = ti.get_pointee().get_canonical()
                return f"POINTER({CTBase.ctype2ctypes(tti)})*{t.get_array_size()}"
            return f"{CTBase.ctype2ctypes(ti)}*{t.get_array_size()}"
        match t.get_canonical().kind:
            case TypeKind.CHAR_S:
                return "c_int8"
            case TypeKind.UCHAR:
                return "c_uint8"
            case TypeKind.SCHAR:
                return "c_int8"
            case TypeKind.SHORT:
                return "c_int16"
            case TypeKind.USHORT:
                return "c_uint16"
            case TypeKind.INT:
                return "c_int32"
            case TypeKind.UINT:
                return "c_uint32"
            case TypeKind.LONG:
                return "c_int64"
            case TypeKind.ULONG:
                return "c_uint64"
            case TypeKind.LONGLONG:
                return "c_int64"
            case TypeKind.ULONGLONG:
                return "c_uint64"
            case TypeKind.FLOAT:
                return "c_float"
            case TypeKind.DOUBLE:
                return "c_double"
            case TypeKind.VOID:
                return "None"
            case TypeKind.ENUM:
                return 'c_int32'
            case TypeKind.BOOL:
                return 'bool'
        print("unhandled ctype2ctypes", t.get_canonical().kind)
        assert False

    @staticmethod
    def ctype2ctype(t):
        if t.kind == TypeKind.ELABORATED:
            return CTBase.getName(t.get_declaration())
        if t.kind == TypeKind.RECORD:
            return CTBase.getName(t.get_declaration())
        if t.kind == TypeKind.POINTER:
            ti = t.get_pointee().get_canonical()
            if ti.kind == TypeKind.RECORD:
                # struct/union
                return f"{CTBase.ctype2ctype(ti)} *"
            elif ti.kind == TypeKind.FUNCTIONPROTO:
                #function
                argtypes = []
                argnames = []
                for arg in ti.argument_types():
                    argtypes.append(CTBase.ctype2ctype(arg))
                    argnames.append(arg.spelling)
                argtypes = ", ".join(argtypes)
                return f"CFUNCTYPE({CTBase.ctype2ctype(ti.get_result())}, {argtypes})"
            elif ti.kind == TypeKind.FUNCTIONNOPROTO:
                return f"CFUNCTYPE({CTBase.ctype2ctype(ti.get_result())})"
            # simple type
            return f"POINTER({CTBase.ctype2ctype(ti)})"
        elif t.kind == TypeKind.CONSTANTARRAY:
            ti = t.get_array_element_type()
            if ti.kind == TypeKind.POINTER:
                tti = ti.get_pointee().get_canonical()
                return f"POINTER({CTBase.ctype2ctype(tti)})*{t.get_array_size()}"
            return f"{CTBase.ctype2ctype(ti)}*{t.get_array_size()}"
        match t.get_canonical().kind:
            case TypeKind.CHAR_S:
                return "char"
            case TypeKind.UCHAR:
                return "unsigned char"
            case TypeKind.SCHAR:
                return "signed char"
            case TypeKind.SHORT:
                return "short"
            case TypeKind.USHORT:
                return "unsigned short"
            case TypeKind.INT:
                return "int"
            case TypeKind.UINT:
                return "unsigned int"
            case TypeKind.LONG:
                return "long"
            case TypeKind.ULONG:
                return "unsigned long"
            case TypeKind.LONGLONG:
                return "longlong"
            case TypeKind.ULONGLONG:
                return "unsigned longlong"
            case TypeKind.FLOAT:
                return "float"
            case TypeKind.DOUBLE:
                return "double"
            case TypeKind.VOID:
                return "void"
            case TypeKind.ENUM:
                return 'int'
            case TypeKind.BOOL:
                return 'bool'
        print("unhandled ctype2ctype", t.get_canonical().kind)
        assert False


class CTVar(CTBase):
    def __init__(self, namespace, ctype, name):
        super().__init__(namespace)
        self.ctype = ctype
        self.name = name

    def write_cpp(self, fp):
        ctype = CTBase.ctype2ctype(self.ctype)
        fp.write(f"""\
    m.def("{self.namespace}_{self.name}", []({ctype} value) {{
        {self.namespace}{self.name} = value;
    }});
""")


class CTEnum(CTBase):
    def __init__(self, namespace, name):
        super().__init__(namespace)
        self.name = name
        self.children = []

    def add(self, name, value):
        elem = (name, value)
        self.children.append(elem)

    def write_py_children(self, fp):
        for name, value in self.children:
            fp.write(f"""\
    {name} = {value}
""")

    def write_py(self, fp):
        fp.write(f"""
class {self.name}(c_int):
""")
        self.write_py_children(fp)

    def write_cpp(self, fp):
        fp.write(f"""
    py::enum_<{self.namespace}{self.name}>(m, "{self.name}")
""")
        for name, value in self.children:
            fp.write(f"""\
        .value("{name}", {self.namespace}{self.name}::{name})
""")
        fp.write(f"""
    ;
""")


class CTUnionStruct(CTBase):
    def __init__(self, namespace, name, align, size):
        super().__init__(namespace)
        self.name = name
        self.align = align
        self.size = size
        self.children = []
        self.hasforward = False
        self.constructors = []
        self.functions = []

    def add(self, ctype, name):
        self.children.append((ctype, name))

    def write_py(self, fp, base):
        if not self.children:
            fp.write(f"""
class {self.name}({base}):
    pass
""")
            return
        if self.hasforward:
            fp.write(f"""
{self.name}._pack_ = {self.align}
{self.name}._fields_ = [
""")
        else:
            fp.write(f"""
class {self.name}({base}):
    _pack_ = {self.align}
    _fields_ = [
""")
        for ctype, name  in self.children:
            ctypestype = CTBase.ctype2ctypes(ctype)
            fp.write(f"""\
        ("{name}", {ctypestype}),
""")
        fp.write(f"""\
    ]
assert sizeof({self.name}) == {self.size}
""")

    def write_cpp(self, fp):
        fp.write(f"""\
    py::class_<{self.namespace}{self.name}>(m, "{self.name}")
""")                
        for ctype, name in self.children:
            fp.write(f"""\
        .def_readwrite("{name}", &{self.namespace}{self.name}::{name})
""")
        for access, argtypes, argnames in self.constructors:
            argtypes = [ CTBase.ctype2ctype(t) for t in argtypes ]
            argtypes = ', '.join(argtypes)
            fp.write(f"""\
        .def(py::init<{argtypes}>())
""")
        for access, result, name, argtypes, argnames in self.functions:
            fp.write(f"""\
        .def("{name}", &{self.namespace}{self.name}::{name})
""")
        fp.write(f"""\
    ;
""")


class CTUnion(CTUnionStruct):
    def write_py(self, fp): # pylint: disable=arguments-differ
        super().write_py(fp, "Union")


class CTStructure(CTUnionStruct):
    def write_py(self, fp): # pylint: disable=arguments-differ
        super().write_py(fp, "Structure")

    def Constructor(self, access, argtypes, argnames):
        self.constructors.append((access, argtypes, argnames))

    def Function(self, access, result, name, argtypes, argnames):
        self.functions.append((access, result, name, argtypes, argnames))


class CTFunction(CTBase):
    def __init__(self, namespace, name, result, argtypes, argnames):
        super().__init__(namespace)
        self.name = name
        self.result = result
        self.argtypes = argtypes
        self.argnames = argnames

    def write_py(self, fp):
        result = CTBase.ctype2ctypes(self.result)
        argtypes = [ CTBase.ctype2ctypes(t) for t in self.argtypes]
        argtypes = ", ".join(argtypes)
        fp.write(f"""\
        self.{self.name} = CFUNCTYPE({result}, {argtypes})(("{self.name}", self.hdll))
""")
    def decorated(self, fp):
        result = CTBase.ctype2ctypes(self.result)
        argtypes = [ CTBase.ctype2ctypes(t) for t in self.argtypes]
        args = []
        for i in range(len(self.argnames)):
            args.append(f"{self.argnames[i]}: {argtypes[i]}")
        args = ', '.join(args)
        argtypes = ", ".join(argtypes)
        argnames = ", ".join(self.argnames)
        fp.write(f"""
        @cdecl({result}, {argtypes})
        def {self.name}({args}):
            return {self.name}._api_({argnames})
""")

    def decorated_def(self, fp):
        fp.write(f"""\
        self.{self.name} = {self.name}
""")


class CTTypedef(CTBase):
    def __init__(self, namespace, ctype, name):
        super().__init__(namespace)
        self.ctype = ctype
        self.name = name

    def write_py(self, fp):
        if self.name != self.ctype:
            ctype = CTBase.ctype2ctypes(self.ctype)
            fp.write(f"""\
{self.name} = {ctype}
""")

    def write_cpp(self, fp):
        if self.name != self.ctype:
            ctype = CTBase.ctype2ctypes(self.ctype)
            fp.write(f"""\
{self.name} = {ctype}
""")


class CTClass(CTBase):
    def __init__(self, namespace, name):
        super().__init__(namespace)
        self.name = name
        self.constructors = []
        self.functions = []
        self.variables = []

    def Constructor(self, access, argtypes, argnames):
        self.constructors.append((access, argtypes, argnames))

    def Function(self, access, result, name, argtypes, argnames):
        self.functions.append((access, result, name, argtypes, argnames))

    def Variable(self, access, result, name):
        self.variables.append((access, result, name))

    def write_py(self, fp):
        fp.write(f"""
'''
class {self.name}:
""")                
        for access, result, name in self.variables:
            fp.write(f"""\
    {name} : {result}
""")                
        for access, argtypes, argnames in self.constructors:
            args = []
            for i in range(len(argnames)):
                args.append(f"{argnames[i]}: {argtypes[i]}")
            args = ', '.join(args)
            fp.write(f"""\
    def __init__(self, {args}):
""")                
        for access, result, name, argtypes, argnames in self.functions:
            args = []
            for i in range(len(argnames)):
                args.append(f"{argnames[i]}: {argtypes[i]}")
            args = ', '.join(args)
            fp.write(f"""\
    def {name}(self, {args}): -> {result}
""")                
        fp.write(f"""
'''
""")

    def write_cpp(self, fp):
        fp.write(f"""\
    py::class_<{self.namespace}{self.name}>(m, "{self.name}")
""")                
        for access, result, name in self.variables:
            fp.write(f"""\
        .def_readwrite("{name}", &{self.namespace}{self.name}::{name})
""")
        for access, argtypes, argnames in self.constructors:
            argtypes = [ CTBase.ctype2ctype(t) for t in argtypes ]
            args = ', '.join(argtypes)
            fp.write(f"""\
        .def(py::init<{args}>())
""")
        for access, result, name, argtypes, argnames in self.functions:
            fp.write(f"""\
        .def("{name}", &{self.namespace}{self.name}::{name})
""")
        fp.write(f"""\
    ;
""")

severity2text = {
    Diagnostic.Ignored: "",
    Diagnostic.Note: "note",
    Diagnostic.Warning: "warning",
    Diagnostic.Error: "error",
    Diagnostic.Fatal: "fatal",
}


class ClangParse:
    def __init__(self):
        self.index = None
        self.tu = None
        self.diags = None
        self.source_path = None
        self.warnings = 0
        self.errors = 0
        self.fatals = 0
        self.elements = []
        self.config = None
        self.macros = []
        self.namespace = []

    def parse_file(self, config):
        self.config = config
        src = config["parsesrc"]
        args = config["parseargs"]
        self.source_path = src
        self.index = clang.cindex.Index.create()
        self.tu = self.index.parse(
            path=src,
            args=args,
            options=
                TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD|
                TranslationUnit.PARSE_SKIP_FUNCTION_BODIES
        )
        self.diags = self.tu.diagnostics
        for diag in self.diags:
            if diag.severity == Diagnostic.Warning:
                self.warnings += 1
            elif diag.severity == Diagnostic.Error:
                self.errors += 1
            elif diag.severity == Diagnostic.Fatal:
                self.fatals += 1

            logger.debug("%s:%d,%d: %s: %s", diag.location.file, diag.location.line, diag.location.column, severity2text.get(diag.severity), diag.spelling)

    def parse_buffer(self, config, buf):
        self.config = config
        src = config["parsesrc"]
        args = config["parseargs"]
        self.source_path = src
        self.index = clang.cindex.Index.create()
        self.tu = self.index.parse(
            path=src,
            args=args,
            unsaved_files=[(src, buf)],
            options=
                TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD|
                TranslationUnit.PARSE_SKIP_FUNCTION_BODIES
        )
        self.diags = self.tu.diagnostics
        for diag in self.diags:
            if diag.severity == Diagnostic.Warning:
                self.warnings += 1
            elif diag.severity == Diagnostic.Error:
                self.errors += 1
            elif diag.severity == Diagnostic.Fatal:
                self.fatals += 1

            logger.debug("%s:%d,%d: %s: %s", diag.location.file, diag.location.line, diag.location.column, severity2text.get(diag.severity), diag.spelling)

    def debugCursor(self, cursor, n=1):
        # pylint: disable=unreachable
        logger.debug('%scursor: spelling: %s kind:%s type.kind:%s',
            ' '*n,
            cursor.spelling, 
            cursor.kind.name,
            cursor.type.kind.name)
        for child in cursor.get_children():
            self.debugCursor(child, n+1)
        return

        for token in cursor.get_tokens():
            logger.debug('token.spelling: %s', token.spelling)
            logger.debug('token.kind: %s', token.kind.name)
            #logger.debug('token.type.kind: %s', token.type.kind.name)

    def checkparseinclude(self, cursor):
        if cursor.location.file and cursor.location.file.name not in self.config["parseinclude"]:
            #logger.debug("skip file:%s" % cursor.location.file)
            return False
        return True

    def visitor(self, cursor=None):
        if cursor is None:
            cursor = self.tu.cursor

        if not self.checkparseinclude(cursor):
            return

        for child in cursor.get_children():
            if not self.checkparseinclude(child):
                continue

            # Check if a visit_EXPR_TYPE member exists in the given object and call it
            # passing the current child element.
            #print(child.kind)
            kind_name = str(child.kind)
            if child.kind == CursorKind.NAMESPACE:
                self.namespace.append(child.spelling)
            elif child.kind not in (CursorKind.MACRO_DEFINITION, CursorKind.MACRO_INSTANTIATION):
                #print(child.kind, cursor.spelling)
                pass
            element = kind_name[kind_name.find(".")+1:]
            method_name = f"visit_{element}"
            func = getattr(self, method_name, None)
            try:
                if func:
                    if func(child):
                        if child.kind == CursorKind.NAMESPACE:
                            self.namespace.pop()
                        continue
#                    else:
#                        print('unhandled:', child.kind)
                elif child.kind != CursorKind.NAMESPACE:
                    tokens = [t.spelling for t in child.get_tokens()]
                    logger.error(f'No handler for: kind:{child.kind} tokens:{tokens}')
            except Exception as exc: # pylint: disable=broad-except
                filename = 'unknown'
                if child.location.file and child.location.file.name:
                    filename = child.location.file.name
                logger.exception('unhandled in %s', filename, exc_info=exc)
                self.debugCursor(child)
                if child.kind == CursorKind.NAMESPACE:
                    self.namespace.pop()
                continue
            # Same as before but we pass to the member any literal expression.
            #method_name = "visit_LITERAL"
            #if child.kind >= CursorKind.INTEGER_LITERAL and child.kind <= CursorKind.STRING_LITERAL:
            #    func = getattr(obj, method_name, None)
            #    if func and func(child):
            #        continue
            try:
                self.visitor(cursor=child)
            finally:
                if child.kind == CursorKind.NAMESPACE:
                    self.namespace.pop()

    def UnionStruct(self, elem, cursor):
        for child in cursor.get_children():
            if child.kind == CursorKind.UNION_DECL:
                #self.debugCursor(child)
                self.visit_UNION_DECL(child)
                continue
            elif child.kind == CursorKind.STRUCT_DECL:
                self.visit_STRUCT_DECL(child)
                continue
            if child.kind == CursorKind.CONSTRUCTOR:
                argnames = []
                argtypes = []
                for arg in child.get_children():
                    argtypes.append(arg.type)
                    argnames.append(arg.spelling)
                elem.Constructor(child.access_specifier, argtypes, argnames)
                continue
            elif child.kind == CursorKind.CXX_METHOD:
                argnames = []
                argtypes = []
                for arg in child.get_children():
                    argtypes.append(arg.type)
                    argnames.append(arg.spelling)
                result = child.result_type.get_canonical()
                elem.Function(child.access_specifier, result, child.spelling, argtypes, argnames)
                continue
            if child.kind != CursorKind.FIELD_DECL:
                tokens = [t.spelling for t in child.get_tokens()]
                logger.error(F"Failed child.kind: {child.kind} != CursorKind.FIELD_DECL tokens: {tokens}")
                self.debugCursor(child)
                continue
            field_name = child.spelling
            t = child.type
            if t.kind == TypeKind.POINTER:
                ti = t.get_pointee().get_canonical()
                if ti.kind == TypeKind.RECORD:
                    elem.add(t, field_name)
                elif ti.kind == TypeKind.FUNCTIONPROTO:
                    elem.add(t, field_name)
                    #t.spelling
                else:
                    elem.add(t, field_name)
            elif t.kind == TypeKind.CONSTANTARRAY:
                elem.add(t, field_name)
            else:
                elem.add(t, field_name)
        self.elements.append(elem)

    def visit_n_o_p(self, cursor):
        # pylint: disable=unreachable
        return False
        self.debugCursor(cursor)

    visit_INCLUSION_DIRECTIVE = visit_n_o_p
    visit_TRANSLATION_UNIT = visit_n_o_p

    def visit_VAR_DECL(self, cursor):
        elem = CTVar(self.namespace, cursor.type, cursor.spelling)
        self.elements.append(elem)
        return True

    def visit_ENUM_DECL(self, cursor):
        elem = CTEnum(self.namespace, cursor.spelling)
        for child in cursor.get_children():
            if child.kind == CursorKind.ENUM_CONSTANT_DECL:
                elem.add(child.displayname, child.enum_value)
            else:
                tokens = [t.spelling for t in child.get_tokens()]
                logger.error(f"Failed enum: displayname:{child.displayname} kind:{child.kind} value:{child.enum_value} tokens:{tokens}")
                self.debugCursor(child)
                assert False
        self.elements.append(elem)
        return True

    def visit_UNION_DECL(self, cursor):
        field_name = cursor.spelling
        if field_name.find('(') > 0:
            field_name = f'unnamed_{cursor.hash}'
        elem = CTUnion(self.namespace, field_name, cursor.type.get_align(), cursor.type.get_size())
        self.UnionStruct(elem, cursor)
        for i in range(len(self.elements)-1):
            if isinstance(elem, CTUnion) and self.elements[i].name == elem.name:
                elem.hasforward = 1
                break
        return True

    def visit_STRUCT_DECL(self, cursor):
        field_name = cursor.spelling
        if field_name.find('(') > 0:
            field_name = f'unnamed_{cursor.hash}'
        elem = CTStructure(self.namespace, field_name, cursor.type.get_align(), cursor.type.get_size())
        self.UnionStruct(elem, cursor)
        for i in range(len(self.elements)-1):
            if isinstance(elem, CTStructure) and self.elements[i].name == elem.name:
                elem.hasforward = 1
                break
        return True

    def known_macro(self, name):
        for m in self.macros:
            if m[0] == name:
                return True
        return False

    def visit_MACRO_DEFINITION(self, cursor):
        e = cursor.extent.start
        if not e.file or e.file.name not in self.config["parseinclude"]:
            return True
        tokens = list(cursor.get_tokens())
        s = [str(tokens[0].spelling)]
        ok = True
        for t in tokens[1:]:
            if t.kind == TokenKind.IDENTIFIER:
                if not self.known_macro(t.spelling):
                    ok = False
            elif not t.kind in (TokenKind.PUNCTUATION, TokenKind.LITERAL):
                ok = False
            ss = str(t.spelling)
            if ss == 'NULL':
                ss = 'None'
            if t.kind == TokenKind.LITERAL:
                if ss[-2:] == 'UL':
                    ss = ss[:-2]
                elif ss[-1] in 'UL':
                    ss = ss[:-1]
            s.append(ss)
        if not ok:
            logger.warning('unhandled macro spelling:%s kind:%s, tokens:%s', t.spelling, t.kind, s)
            s[0] = '#'+s[0]
        else:
            s.insert(1, '=')
            if len(s) == 2:
                s.append('True')
        self.macros.append((s[0], ' '.join(s)))
        return True

    def visit_MACRO_INSTANTIATION(self, cursor):
        # pylint: disable=unreachable
        return True
        e = cursor.extent.start
        if not e.file or e.file.name not in self.config["parseinclude"]:
            return True
        def slc(e):
            return (e.file.name, e.line, e.column)
        print(
            'MACRO_INSTANTIATION', cursor.displayname, #cursor.spelling,
            #cursor.data,
            slc(cursor.extent.start), slc(cursor.extent.end)
        )
        tokens = list(cursor.get_tokens())
        s = ' '.join([str(t.spelling) for t in tokens])
        print(s)
        return True

    def visit_FUNCTION_DECL(self, cursor):
        argnames = []
        argtypes = []
        for arg in cursor.get_arguments():
            argtypes.append(arg.type)
            argnames.append(arg.spelling)
        elem = CTFunction(
            self.namespace, 
            cursor.spelling,
            cursor.result_type.get_canonical(),
            argtypes,
            argnames,
        )
        self.elements.append(elem)
        return True

    def visit_TYPEDEF_DECL(self, cursor):
        field_name = cursor.spelling
        t = cursor.type
        ti = t.get_canonical()
        if ti.kind == TypeKind.RECORD:
            pass
        elif ti.kind == TypeKind.POINTER:
            ti = t.get_canonical()
        elif ti.kind == TypeKind.CONSTANTARRAY:
            pass
        else:
            ti = t
        elem = CTTypedef(self.namespace, ti, field_name)
        self.elements.append(elem)
        return True

    def visit_CLASS_DECL(self, cursor):
        elem = CTClass(self.namespace, cursor.spelling)
        for child in cursor.get_children():
            if child.kind == CursorKind.CONSTRUCTOR:
                argnames = []
                argtypes = []
                for arg in child.get_children():
                    argtypes.append(arg.type)
                    argnames.append(arg.spelling)
                elem.Constructor(child.access_specifier, argtypes, argnames)
            elif child.kind == CursorKind.FIELD_DECL:
                field_name = child.spelling
                t = child.type
                if t.kind == TypeKind.POINTER:
                    ti = t.get_pointee().get_canonical()
                    if ti.kind == TypeKind.RECORD:
                        elem.Variable(child.access_specifier, t, field_name)
                    elif ti.kind == TypeKind.FUNCTIONPROTO:
                        elem.Variable(child.access_specifier, t, field_name)
                        #t.spelling
                    else:
                        elem.Variable(child.access_specifier, t, field_name)
                elif t.kind == TypeKind.CONSTANTARRAY:
                    elem.Variable(child.access_specifier, t, field_name)
                else:
                    elem.Variable(child.access_specifier, t, field_name)
            elif child.kind == CursorKind.CXX_METHOD:
                argnames = []
                argtypes = []
                for arg in child.get_children():
                    argtypes.append(arg.type)
                    argnames.append(arg.spelling)
                elem.Function(child.access_specifier, child.result_type.get_canonical(), child.spelling, argtypes, argnames)
        self.elements.append(elem)

        return False

    def visit_TYPE_REF(self, cursor):
        return True
