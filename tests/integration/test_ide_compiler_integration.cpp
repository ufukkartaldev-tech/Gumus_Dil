#include <gtest/gtest.h>
#include "../../src/compiler/main.cpp" // Include main compiler functionality
#include <fstream>
#include <filesystem>
#include <sstream>

class IDECompilerIntegrationTest : public ::testing::Test {
protected:
    std::string tempDir;
    std::string testFile;
    
    void SetUp() override {
        // Create temporary directory for test files
        tempDir = std::filesystem::temp_directory_path() / "gumusdil_test";
        std::filesystem::create_directories(tempDir);
        testFile = tempDir + "/test_program.tr";
    }
    
    void TearDown() override {
        // Clean up temporary files
        std::filesystem::remove_all(tempDir);
    }
    
    void writeTestFile(const std::string& content) {
        std::ofstream file(testFile);
        file << content;
        file.close();
    }
    
    std::string runCompiler(const std::vector<std::string>& args) {
        // Capture stdout
        std::ostringstream output;
        std::streambuf* oldCout = std::cout.rdbuf();
        std::cout.rdbuf(output.rdbuf());
        
        // Prepare arguments
        std::vector<const char*> argv;
        argv.push_back("gumus"); // Program name
        for (const auto& arg : args) {
            argv.push_back(arg.c_str());
        }
        
        // Run compiler main function
        int result = 0; // Would call main function here
        
        // Restore stdout
        std::cout.rdbuf(oldCout);
        
        return output.str();
    }
};

// 🧪 File Compilation Testi
TEST_F(IDECompilerIntegrationTest, FileCompilation) {
    writeTestFile(R"(
        değişken mesaj = "Merhaba Dünya"
        yazdır(mesaj)
    )");
    
    std::string output = runCompiler({testFile});
    
    // Should compile and run successfully
    EXPECT_TRUE(output.find("Merhaba Dünya") != std::string::npos);
}

// 🧪 Syntax Error Reporting Testi
TEST_F(IDECompilerIntegrationTest, SyntaxErrorReporting) {
    writeTestFile(R"(
        değişken x = 
        yazdır(x)
    )");
    
    std::string output = runCompiler({testFile});
    
    // Should report syntax error with line number
    EXPECT_TRUE(output.find("error") != std::string::npos || 
                output.find("ERROR") != std::string::npos);
    EXPECT_TRUE(output.find("2") != std::string::npos); // Line number
}

// 🧪 Runtime Error Reporting Testi
TEST_F(IDECompilerIntegrationTest, RuntimeErrorReporting) {
    writeTestFile(R"(
        değişken x = 10
        değişken y = 0
        yazdır(x / y)
    )");
    
    std::string output = runCompiler({testFile});
    
    // Should report runtime error
    EXPECT_TRUE(output.find("error") != std::string::npos || 
                output.find("ERROR") != std::string::npos);
}

// 🧪 Debug Mode Testi
TEST_F(IDECompilerIntegrationTest, DebugMode) {
    writeTestFile(R"(
        değişken x = 5
        eğer (x > 3) {
            yazdır("x büyük")
        }
        yazdır("bitti")
    )");
    
    std::string output = runCompiler({"--debug", testFile});
    
    // Debug mode should provide additional information
    EXPECT_TRUE(output.find("DEBUG") != std::string::npos ||
                output.find("debug") != std::string::npos);
}

// 🧪 AST Dump Testi
TEST_F(IDECompilerIntegrationTest, ASTDump) {
    writeTestFile(R"(
        fonksiyon topla(a, b) {
            dön a + b
        }
        
        değişken sonuc = topla(5, 3)
    )");
    
    std::string output = runCompiler({"--dump-ast", testFile});
    
    // Should output AST in JSON format
    EXPECT_TRUE(output.find("{") != std::string::npos);
    EXPECT_TRUE(output.find("FunctionStmt") != std::string::npos ||
                output.find("function") != std::string::npos);
}

// 🧪 Memory Dump Testi
TEST_F(IDECompilerIntegrationTest, MemoryDump) {
    writeTestFile(R"(
        değişken liste = [1, 2, 3, 4, 5]
        değişken obj = {
            "isim": "test",
            "değer": 42
        }
    )");
    
    std::string output = runCompiler({"--dump-memory", testFile});
    
    // Should output memory information
    EXPECT_TRUE(output.find("memory") != std::string::npos ||
                output.find("MEMORY") != std::string::npos);
}

// 🧪 Multiple File Compilation Testi
TEST_F(IDECompilerIntegrationTest, MultipleFileCompilation) {
    // Create main file
    writeTestFile(R"(
        dahil_et("helper.tr")
        
        değişken sonuc = yardımcı_fonksiyon(10)
        yazdır(sonuc)
    )");
    
    // Create helper file
    std::string helperFile = tempDir + "/helper.tr";
    std::ofstream helper(helperFile);
    helper << R"(
        fonksiyon yardımcı_fonksiyon(x) {
            dön x * 2
        }
    )";
    helper.close();
    
    std::string output = runCompiler({testFile});
    
    // Should compile and link multiple files
    EXPECT_TRUE(output.find("20") != std::string::npos);
}

// 🧪 Library Integration Testi
TEST_F(IDECompilerIntegrationTest, LibraryIntegration) {
    writeTestFile(R"(
        dahil_et("matematik.tr")
        
        değişken x = mat_kök(16)
        değişken y = mat_üs(2, 3)
        
        yazdır("Kök: " + x)
        yazdır("Üs: " + y)
    )");
    
    std::string output = runCompiler({testFile});
    
    // Should use library functions
    EXPECT_TRUE(output.find("Kök: 4") != std::string::npos);
    EXPECT_TRUE(output.find("Üs: 8") != std::string::npos);
}

// 🧪 UTF-8 File Handling Testi
TEST_F(IDECompilerIntegrationTest, UTF8FileHandling) {
    writeTestFile(R"(
        değişken türkçe = "ğüşıöçĞÜŞİÖÇ"
        değişken mesaj = "Türkçe karakterler: " + türkçe
        yazdır(mesaj)
    )");
    
    std::string output = runCompiler({testFile});
    
    // Should handle UTF-8 characters correctly
    EXPECT_TRUE(output.find("ğüşıöçĞÜŞİÖÇ") != std::string::npos);
}

// 🧪 Large File Compilation Testi
TEST_F(IDECompilerIntegrationTest, LargeFileCompilation) {
    std::ostringstream largeProgram;
    
    // Generate a large program
    largeProgram << "// Large program test\n";
    for (int i = 0; i < 1000; i++) {
        largeProgram << "değişken var" << i << " = " << i << "\n";
    }
    
    largeProgram << R"(
        fonksiyon toplam() {
            değişken sonuc = 0
    )";
    
    for (int i = 0; i < 1000; i++) {
        largeProgram << "    sonuc = sonuc + var" << i << "\n";
    }
    
    largeProgram << R"(
            dön sonuc
        }
        
        yazdır("Toplam: " + toplam())
    )";
    
    writeTestFile(largeProgram.str());
    
    auto start = std::chrono::high_resolution_clock::now();
    std::string output = runCompiler({testFile});
    auto end = std::chrono::high_resolution_clock::now();
    
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    // Should compile large files within reasonable time (< 10 seconds)
    EXPECT_LT(duration.count(), 10000);
    
    // Should calculate correct sum: 0+1+2+...+999 = 499500
    EXPECT_TRUE(output.find("499500") != std::string::npos);
}

// 🧪 Command Line Arguments Testi
TEST_F(IDECompilerIntegrationTest, CommandLineArguments) {
    writeTestFile(R"(
        yazdır("Program başladı")
        yazdır("Argüman sayısı: " + args.length())
        
        değişken i = 0
        döngü (i < args.length()) {
            yazdır("Arg[" + i + "]: " + args[i])
            i = i + 1
        }
    )");
    
    std::string output = runCompiler({testFile, "arg1", "arg2", "arg3"});
    
    // Should handle command line arguments
    EXPECT_TRUE(output.find("Program başladı") != std::string::npos);
    EXPECT_TRUE(output.find("Argüman sayısı: 3") != std::string::npos);
    EXPECT_TRUE(output.find("Arg[0]: arg1") != std::string::npos);
}

// 🧪 Performance Profiling Testi
TEST_F(IDECompilerIntegrationTest, PerformanceProfiling) {
    writeTestFile(R"(
        fonksiyon fibonacci(n) {
            eğer (n <= 1) {
                dön n
            } değilse {
                dön fibonacci(n - 1) + fibonacci(n - 2)
            }
        }
        
        değişken start = getCurrentTime()
        değişken result = fibonacci(20)
        değişken end = getCurrentTime()
        
        yazdır("Fibonacci(20) = " + result)
        yazdır("Süre: " + (end - start) + "ms")
    )");
    
    std::string output = runCompiler({"--profile", testFile});
    
    // Should provide profiling information
    EXPECT_TRUE(output.find("Fibonacci(20) = 6765") != std::string::npos);
    EXPECT_TRUE(output.find("Süre:") != std::string::npos);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}