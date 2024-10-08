#!/usr/bin/env vpython3
import sys
import json
import logging
import clang.cindex
from clang.cindex import Diagnostic, CursorKind, TokenKind, TranslationUnit, TypeKind

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG, 
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)

class CTEnum:
    def __init__(self, name):
        self.name = name
        self.children = []
    def add(self, name, value):
        elem = (name, value)
        self.children.append(elem)
    def write(self, fp):
        fp.write(f"""
class {self.name}(c_int):
""")
        self.writechildren()
    def writechildren(self, fp):
        for name, value in self.children:
            fp.write(f"""\
    {name} = {value}
""")

class CTUnionStruct:
    def __init__(self, name, align, size):
        self.name = name
        self.align = align
        self.size = size
        self.children = []
        self.hasforward = False

    def add(self, name, value):
        elem = (name, value)
        self.children.append(elem)

    def write(self, fp, base):
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
        for name, value in self.children:
            fp.write(f"""\
        ("{name}", {value}),
""")
        fp.write(f"""\
    ]
assert sizeof({self.name}) == {self.size}
""")

class CTUnion(CTUnionStruct):
    def write(self, fp):
        super().write(fp, "Union")

class CTStructure(CTUnionStruct):
    def write(self, fp):
        super().write(fp, "Structure")

class CTFunction:
    def __init__(self, name, type, argtypes, argnames):
        self.name = name
        self.type = type
        self.argtypes = argtypes
        self.argnames = argnames

    def write(self, fp):
        fp.write(f"""\
        self.{self.name} = CFUNCTYPE({self.type}{self.argtypes})(("{self.name}", hdll))
""")
        if 0:
            print("@CFUNCTYPE(%s%s)"%(resulttype, argtypes))
            print("def %s(%s):"%(funcname, argnames))
            print("    %s._api_(%s)"%(funcname, argnames))

class CTTypedef:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def write(self, fp):
        if self.name != self.value:
            fp.write(f"""
{self.name} = {self.value}
""")

def main():
    with open(f"{sys.argv[1]}.json", "rt") as fp:
        config = json.load(fp)
    cls = Clang2ctypes()
    cls.parse_file(config)
    if cls.errors or cls.fatals:
        return
    cls.visitor()
    with open(f"{config['filename']}.py", "wt") as fp:
        fp.write("""\
from ctypes import (
    CDLL, CFUNCTYPE, POINTER,
    Union, Structure, sizeof,
    c_size_t, c_int,
    c_int8, c_uint8,
    c_int16, c_uint16,
    c_int32, c_uint32,
    c_int64, c_uint64,
    c_int64, c_uint64,
    c_float, c_double
)

int8_t = c_int8
int16_t = c_int16
int32_t = c_int32
int64_t = c_int64
uint8_t = c_uint8
uint16_t = c_uint16
uint32_t = c_uint32
uint64_t = c_uint64

size_t = c_size_t
""")
        fp.write("\n")
        noenumclass = config.get("noenumclass", False)
        if noenumclass:
            for elem in cls.elements:
                if isinstance(elem, CTEnum):
                    fp.write(f"""\
{elem.name} = c_int32
""")
            fp.write("""
if 1:
""")
            for elem in cls.elements:
                if isinstance(elem, CTEnum):
                    fp.write(f"""\
    # {elem.name}
""")
                    elem.writechildren(fp)
        else:
            for elem in cls.elements:
                if isinstance(elem, CTEnum):
                    elem.write(fp)

        for elem in cls.elements:
            if not isinstance(elem, CTFunction) and not isinstance(elem, CTEnum):
                elem.write(fp)
        fp.write(f"""
class {config['classname']}:
    def __init__(self, path):
        hdll = self.hdll = CDLL(path)
""")
        for elem in cls.elements:
            if isinstance(elem, CTFunction):
                elem.write(fp)

severity2text = {
    Diagnostic.Ignored: "",
    Diagnostic.Note: "note",
    Diagnostic.Warning: "warning",
    Diagnostic.Error: "error",
    Diagnostic.Fatal: "fatal",
}

class Clang2ctypes:
    def __init__(self):
        self.index = None
        self.tu = None
        self.diags = None
        self.source_path = None
        self.warnings = 0
        self.errors = 0
        self.fatals = 0
        self.total_elements = 0
        self.elements = []
        self.config = None

    def parse_file(self, config):
        self.config = config
        src = config["parsesrc"]
        args = config["parseargs"]
        self.source_path = src
        self.index = clang.cindex.Index.create()
        self.tu = self.index.parse(path=src, args=args, options=TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD|TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
        self.diags = self.tu.diagnostics
        for diag in self.diags:
            if diag.severity == Diagnostic.Warning:
                self.warnings += 1
            elif diag.severity == Diagnostic.Error:
                self.errors += 1
            elif diag.severity == Diagnostic.Fatal:
                self.fatals += 1

            logger.debug("%s:%d,%d: %s: %s" % (diag.location.file, diag.location.line, diag.location.column, severity2text.get(diag.severity), diag.spelling))

    def parse_buffer(self, config, buf):
        self.config = config
        src = config["parsesrc"]
        args = config["parseargs"]
        self.source_path = src
        self.index = clang.cindex.Index.create()
        self.tu = self.index.parse(path=src, args=args, unsaved_files=[(src, buf)])
        self.diags = self.tu.diagnostics
        for diag in self.diags:
            if diag.severity == Diagnostic.Warning:
                self.warnings += 1
            elif diag.severity == Diagnostic.Error:
                self.errors += 1
            elif diag.severity == Diagnostic.Fatal:
                self.fatals += 1

            logger.debug("%s:%d,%d: %s: %s" % (diag.location.file, diag.location.line, diag.location.column, severity2text.get(diag.severity), diag.spelling))

    def debugCursor(self, cursor, n=1):
        logger.debug('%scursor: spelling: %s kind:%s type.kind:%s', ' '*n,
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

    def getName(self, elem):
        field_name = elem.spelling
        if field_name.find('(') > 0:
            field_name = 'unnamed_%s'%elem.hash
        return field_name

    def visitor(self, cursor=None):
        if cursor is None:
            cursor = self.tu.cursor

        if not self.checkparseinclude(cursor):
            return

        for children in cursor.get_children():
            if not self.checkparseinclude(children):
                continue

            self.total_elements += 1

            # Check if a visit_EXPR_TYPE member exists in the given object and call it
            # passing the current children element.
            kind_name = str(children.kind)
            element = kind_name[kind_name.find(".")+1:]
            method_name = "visit_%s" % element
            func = getattr(self, method_name, None)
            try:
                if func and func(children):
                    continue
            except:
                filename = 'unknown'
                if children.location.file and children.location.file.name:
                    filename = children.location.file.name
                logger.exception('unhandled in %s', filename)
                self.debugCursor(children)
                continue
            # Same as before but we pass to the member any literal expression.
            #method_name = "visit_LITERAL"
            #if children.kind >= CursorKind.INTEGER_LITERAL and children.kind <= CursorKind.STRING_LITERAL:
            #    func = getattr(obj, method_name, None)
            #    if func and func(children):
            #        continue

            self.visitor(cursor=children)

    def visit_ENUM_DECL(self, cursor):
        elem = CTEnum(cursor.spelling)
        for cc in cursor.get_children():
            if cc.kind == CursorKind.ENUM_CONSTANT_DECL:
                elem.add(cc.displayname, cc.enum_value)
            else:
                print("enum?", cc.displayname, cc.kind, "=", cc.enum_value)
                assert False
        self.elements.append(elem)
        return True

    def type2ctypes(self, t):
        if t.kind == TypeKind.ELABORATED:
            return self.getName(t.get_declaration())
        if t.kind == TypeKind.RECORD:
            return self.getName(t.get_declaration())
        if t.kind == TypeKind.POINTER:
            ti = t.get_pointee().get_canonical()
            if ti.kind == TypeKind.RECORD:
                # struct/union
                return "POINTER(%s)"%self.type2ctypes(ti)
            elif ti.kind == TypeKind.FUNCTIONPROTO:
                #function
                argtypes = []
                for arg in ti.argument_types():
                    argtypes.append(self.type2ctypes(arg))
                argtypes = ", ".join(argtypes)
                if argtypes:
                    argtypes = ", "+argtypes
                return "CFUNCTYPE(%s%s)"%(self.type2ctypes(ti.get_result()), argtypes)
            elif ti.kind == TypeKind.FUNCTIONNOPROTO:
                return "CFUNCTYPE(%s)"%(self.type2ctypes(ti.get_result()))
            # simple type
            return "POINTER(%s)"%self.type2ctypes(ti)
        elif t.kind == TypeKind.CONSTANTARRAY:
            ti = t.get_array_element_type()
            if ti.kind == TypeKind.POINTER:
                tti = ti.get_pointee().get_canonical()
                return "POINTER(%s)*%s"%(self.type2ctypes(tti), t.get_array_size())
            return "%s*%s"%(self.type2ctypes(ti), t.get_array_size())
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
        print("unhandled type", t.get_canonical().kind)
        assert False

    def UnionStruct(self, elem, cursor):
        for cc in cursor.get_children():
            if cc.kind == CursorKind.UNION_DECL:
                #self.debugCursor(cc)
                self.visit_UNION_DECL(cc)
                continue
            elif cc.kind == CursorKind.STRUCT_DECL:
                self.visit_STRUCT_DECL(cc)
                continue
            assert cc.kind == CursorKind.FIELD_DECL
            field_name = cc.spelling
            t = cc.type
            if t.kind == TypeKind.POINTER:
                ti = t.get_pointee().get_canonical()
                if ti.kind == TypeKind.RECORD:
                    elem.add(field_name, self.type2ctypes(t))
                elif ti.kind == TypeKind.FUNCTIONPROTO:
                    elem.add(field_name, self.type2ctypes(t))
                    #t.spelling
                else:
                    elem.add(field_name, self.type2ctypes(t))
            elif t.kind == TypeKind.CONSTANTARRAY:
                elem.add(field_name, self.type2ctypes(t))
            else:
                elem.add(field_name, self.type2ctypes(t))
        self.elements.append(elem)

    def visit_UNION_DECL(self, cursor):
        field_name = cursor.spelling
        if field_name.find('(') > 0:
            field_name = 'unnamed_%s'%cursor.hash
        elem = CTUnion(field_name, cursor.type.get_align(), cursor.type.get_size())
        self.UnionStruct(elem, cursor)
        for i in range(len(self.elements)-1):
            if isinstance(elem, CTUnion) and self.elements[i].name == elem.name:
                elem.hasforward = 1
                break
        return True

    def visit_STRUCT_DECL(self, cursor):
        field_name = cursor.spelling
        if field_name.find('(') > 0:
            field_name = 'unnamed_%s'%cursor.hash
        elem = CTStructure(field_name, cursor.type.get_align(), cursor.type.get_size())
        self.UnionStruct(elem, cursor)
        for i in range(len(self.elements)-1):
            if isinstance(elem, CTStructure) and self.elements[i].name == elem.name:
                elem.hasforward = 1
                break
        return True

    def visit_MACRO_DEFINITION(self, cursor):
        return True
        self.debugCursor(cursor)
        def slc(e):
            return (e.file.name, e.line, e.column)
        print(
            'MACRO_DEFINITION', cursor.displayname, #cursor.spelling,
            #cursor.data,
            slc(cursor.extent.start), slc(cursor.extent.end)
        )
        tokens = list(cursor.get_tokens())
        s = ' '.join([str(t.spelling) for t in tokens])
        print(len(tokens), s)
        return False

    def visit_MACRO_INSTANTIATION(self, cursor):
        return True
        self.debugCursor(cursor)
        def slc(e):
            return (e.file.name, e.line, e.column)
        print(
            'MACRO_INSTANTIATION', cursor.displayname, #cursor.spelling,
            #cursor.data,
            slc(cursor.extent.start), slc(cursor.extent.end)
        )
        tokens = list(cursor.get_tokens())
        s = ' '.join([str(t.spelling) for t in tokens])
        print(len(tokens), s)
        return False

    def visit_VAR_DECL(self, cursor):
        return True

    def visit_TRANSLATION_UNIT(self, cursor):
        return False

    def visit_FUNCTION_DECL(self, cursor):
        argnames = []
        argtypes = []
        for arg in cursor.get_arguments():
            argtypes.append(self.type2ctypes(arg.type))
            argnames.append(arg.spelling)
        argtypes = ", ".join(argtypes)
        argnames = ", ".join(argnames)
        if argtypes:
            argtypes = ", "+argtypes
        result = cursor.result_type.get_canonical()
        elem = CTFunction(
            cursor.spelling,
            self.type2ctypes(result),
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
            td = self.type2ctypes(ti)
        elif ti.kind == TypeKind.POINTER:
            ti = t.get_canonical()
            td = self.type2ctypes(ti)
        elif ti.kind == TypeKind.CONSTANTARRAY:
            td = self.type2ctypes(ti)
        else:
            td = self.type2ctypes(t)
        elem = CTTypedef(field_name, td)
        self.elements.append(elem)
        return True

main()
