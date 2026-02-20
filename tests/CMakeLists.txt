cmake_minimum_required(VERSION 3.14)
project(GumusTests)

# C++ Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Google Test bul
find_package(GTest REQUIRED)

# Test kaynakları
set(TEST_SOURCES
    test_tokenizer.cpp
    # Gelecekte eklenecek testler:
    # test_interpreter.cpp
    # test_parser.cpp
    # test_native_functions.cpp
)

# Ana proje kaynakları (test için)
set(GUMUS_SOURCES
    ../src/compiler/lexer/tokenizer.cpp
    ../src/compiler/lexer/token.cpp
    ../src/compiler/json_hata.cpp
)

# Test executable oluştur
add_executable(unit_tests ${TEST_SOURCES} ${GUMUS_SOURCES})

# Include directories
target_include_directories(unit_tests PRIVATE 
    ${GTEST_INCLUDE_DIRS}
    ../src
)

# Link libraries
target_link_libraries(unit_tests 
    GTest::GTest
    GTest::Main
)

# Windows için UTF-8 desteği
if(WIN32)
    target_compile_definitions(unit_tests PRIVATE 
        UNICODE
        _UNICODE
    )
endif()

# Testleri çalıştır
enable_testing()
add_test(NAME TokenizerTests COMMAND unit_tests)

# Coverage için (isteğe bağlı)
option(ENABLE_COVERAGE "Enable coverage reporting" OFF)
if(ENABLE_COVERAGE AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(unit_tests PRIVATE --coverage)
    target_link_options(unit_tests PRIVATE --coverage)
endif()

