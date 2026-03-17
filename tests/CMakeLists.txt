cmake_minimum_required(VERSION 3.14)
project(GumusTests)

# C++ Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Google Test bul
find_package(GTest REQUIRED)

# Include directories
include_directories(../src/compiler)
include_directories(../src/compiler/lexer)
include_directories(../src/compiler/parser)
include_directories(../src/compiler/interpreter)
include_directories(../src/compiler/vm)
include_directories(../src/compiler/semantic)

# Compiler source files
set(COMPILER_SOURCES
    ../src/compiler/lexer/tokenizer.cpp
    ../src/compiler/lexer/token.cpp
    ../src/compiler/parser/parser.cpp
    ../src/compiler/parser/ast.cpp
    ../src/compiler/interpreter/interpreter.cpp
    ../src/compiler/interpreter/value.cpp
    ../src/compiler/interpreter/environment.cpp
    ../src/compiler/interpreter/garbage_collector.cpp
    ../src/compiler/interpreter/memory_arena.cpp
    ../src/compiler/vm/vm.cpp
    ../src/compiler/vm/chunk.cpp
    ../src/compiler/vm/compiler.cpp
    ../src/compiler/semantic/resolver.cpp
    ../src/compiler/json_hata.cpp
)

# Unit Tests
add_executable(test_tokenizer 
    test_tokenizer.cpp 
    ${COMPILER_SOURCES}
)
target_link_libraries(test_tokenizer GTest::GTest GTest::Main)

add_executable(test_parser 
    unit/test_parser.cpp 
    ${COMPILER_SOURCES}
)
target_link_libraries(test_parser GTest::GTest GTest::Main)

add_executable(test_interpreter 
    unit/test_interpreter.cpp 
    ${COMPILER_SOURCES}
)
target_link_libraries(test_interpreter GTest::GTest GTest::Main)

add_executable(test_garbage_collector 
    unit/test_garbage_collector.cpp 
    ${COMPILER_SOURCES}
)
target_link_libraries(test_garbage_collector GTest::GTest GTest::Main)

add_executable(test_vm 
    unit/test_vm.cpp 
    ${COMPILER_SOURCES}
)
target_link_libraries(test_vm GTest::GTest GTest::Main)

# Integration Tests
add_executable(test_compiler_pipeline 
    integration/test_compiler_pipeline.cpp 
    ${COMPILER_SOURCES}
)
target_link_libraries(test_compiler_pipeline GTest::GTest GTest::Main)

add_executable(test_ide_compiler_integration 
    integration/test_ide_compiler_integration.cpp 
    ${COMPILER_SOURCES}
)
target_link_libraries(test_ide_compiler_integration GTest::GTest GTest::Main)

# Windows için UTF-8 desteği
if(WIN32)
    target_compile_definitions(test_tokenizer PRIVATE UNICODE _UNICODE)
    target_compile_definitions(test_parser PRIVATE UNICODE _UNICODE)
    target_compile_definitions(test_interpreter PRIVATE UNICODE _UNICODE)
    target_compile_definitions(test_garbage_collector PRIVATE UNICODE _UNICODE)
    target_compile_definitions(test_vm PRIVATE UNICODE _UNICODE)
    target_compile_definitions(test_compiler_pipeline PRIVATE UNICODE _UNICODE)
    target_compile_definitions(test_ide_compiler_integration PRIVATE UNICODE _UNICODE)
endif()

# Testleri çalıştır
enable_testing()
add_test(NAME TokenizerTests COMMAND test_tokenizer)
add_test(NAME ParserTests COMMAND test_parser)
add_test(NAME InterpreterTests COMMAND test_interpreter)
add_test(NAME GarbageCollectorTests COMMAND test_garbage_collector)
add_test(NAME VMTests COMMAND test_vm)
add_test(NAME CompilerPipelineTests COMMAND test_compiler_pipeline)
add_test(NAME IDECompilerIntegrationTests COMMAND test_ide_compiler_integration)

# Test runner target - tüm testleri çalıştır
add_custom_target(run_all_tests
    COMMAND test_tokenizer
    COMMAND test_parser
    COMMAND test_interpreter
    COMMAND test_garbage_collector
    COMMAND test_vm
    COMMAND test_compiler_pipeline
    COMMAND test_ide_compiler_integration
    DEPENDS test_tokenizer test_parser test_interpreter test_garbage_collector test_vm test_compiler_pipeline test_ide_compiler_integration
    COMMENT "Running all C++ compiler tests"
)

# Coverage için (isteğe bağlı)
option(ENABLE_COVERAGE "Enable coverage reporting" OFF)
if(ENABLE_COVERAGE AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(test_tokenizer PRIVATE --coverage)
    target_link_options(test_tokenizer PRIVATE --coverage)
    target_compile_options(test_parser PRIVATE --coverage)
    target_link_options(test_parser PRIVATE --coverage)
    target_compile_options(test_interpreter PRIVATE --coverage)
    target_link_options(test_interpreter PRIVATE --coverage)
    target_compile_options(test_garbage_collector PRIVATE --coverage)
    target_link_options(test_garbage_collector PRIVATE --coverage)
    target_compile_options(test_vm PRIVATE --coverage)
    target_link_options(test_vm PRIVATE --coverage)
    target_compile_options(test_compiler_pipeline PRIVATE --coverage)
    target_link_options(test_compiler_pipeline PRIVATE --coverage)
    target_compile_options(test_ide_compiler_integration PRIVATE --coverage)
    target_link_options(test_ide_compiler_integration PRIVATE --coverage)
endif()

