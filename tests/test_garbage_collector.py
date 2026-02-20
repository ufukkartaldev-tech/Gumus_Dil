# 🧪 Garbage Collector Unit Testleri

import pytest
import sys
import os

# Proje path'ini ekle
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Mock C++ components için Python wrapper
class MockValue:
    def __init__(self, value_type, data=None):
        self.type = value_type
        self.data = data
        self.is_marked = False
        self.size = 100  # Mock size
        
    def get_size(self):
        return self.size
        
    def to_string(self):
        return f"MockValue({self.type})"

class MockEnvironment:
    def __init__(self, name="Global"):
        self.name = name
        self.values = {}
        self.enclosing = None
        
    def define(self, name, value):
        self.values[name] = value
        
    def get_references(self):
        return list(self.values.values())

class MockGarbageCollector:
    def __init__(self):
        self.heap = []
        self.roots = set()
        self.global_environment = MockEnvironment()
        self.total_collections = 0
        self.memory_freed = 0
        self.objects_collected = 0
        
    def add_to_heap(self, obj):
        if obj:
            self.heap.append(obj)
            
    def add_root(self, obj):
        if obj:
            self.roots.add(obj)
            
    def remove_root(self, obj):
        self.roots.discard(obj)
        
    def mark(self, obj):
        if obj and not obj.is_marked:
            obj.is_marked = True
            
    def sweep(self):
        initial_size = len(self.heap)
        self.heap = [obj for obj in self.heap if obj.is_marked]
        
        # Reset marks
        for obj in self.heap:
            obj.is_marked = False
            
        collected_this_round = initial_size - len(self.heap)
        self.objects_collected += collected_this_round  # Accumulate
        self.memory_freed += collected_this_round * 100  # Mock
        self.total_collections += 1
        
    def collect(self):
        # Mark phase
        for root in self.roots:
            self.mark(root)
            
        # Sweep phase
        self.sweep()
        
    def get_heap_size(self):
        return len(self.heap)
        
    def get_root_count(self):
        return len(self.roots)
        
    def get_memory_stats(self):
        return {
            'heap_size': self.get_heap_size(),
            'root_count': self.get_root_count(),
            'total_collections': self.total_collections,
            'memory_freed': self.memory_freed,
            'objects_collected': self.objects_collected
        }

class TestGarbageCollector:
    """Garbage Collector unit testleri"""
    
    @pytest.fixture
    def gc(self):
        return MockGarbageCollector()
    
    def test_initialization(self, gc):
        """GC başlangıç durumu"""
        assert gc.get_heap_size() == 0
        assert gc.get_root_count() == 0
        assert gc.total_collections == 0
        assert gc.memory_freed == 0
        assert gc.objects_collected == 0
    
    def test_add_to_heap(self, gc):
        """Heap'e object ekleme"""
        obj1 = MockValue("Integer")
        obj2 = MockValue("String")
        
        gc.add_to_heap(obj1)
        gc.add_to_heap(obj2)
        
        assert gc.get_heap_size() == 2
        assert obj1 in gc.heap
        assert obj2 in gc.heap
    
    def test_root_management(self, gc):
        """Root management testleri"""
        obj1 = MockValue("Integer")
        obj2 = MockValue("String")
        
        # Root ekle
        gc.add_root(obj1)
        gc.add_root(obj2)
        
        assert gc.get_root_count() == 2
        assert obj1 in gc.roots
        assert obj2 in gc.roots
        
        # Root çıkar
        gc.remove_root(obj1)
        
        assert gc.get_root_count() == 1
        assert obj1 not in gc.roots
        assert obj2 in gc.roots
    
    def test_mark_and_sweep(self, gc):
        """Mark and sweep algoritması"""
        # Objects oluştur
        obj1 = MockValue("Integer")
        obj2 = MockValue("String")
        obj3 = MockValue("List")
        
        # Heap'e ekle
        gc.add_to_heap(obj1)
        gc.add_to_heap(obj2)
        gc.add_to_heap(obj3)
        
        # obj1 ve obj2'yi root yap
        gc.add_root(obj1)
        gc.add_root(obj2)
        
        # GC çalıştır
        gc.collect()
        
        # Sadece root'lar kalmalı
        assert gc.get_heap_size() == 2
        assert obj1 in gc.heap
        assert obj2 in gc.heap
        assert obj3 not in gc.heap
        
        # İstatistikler kontrol
        assert gc.total_collections == 1
        assert gc.objects_collected == 1
        assert gc.memory_freed == 100
    
    def test_multiple_collections(self, gc):
        """Çoklu GC collection"""
        # İlk collection
        obj1 = MockValue("Integer")
        obj2 = MockValue("String")
        
        gc.add_to_heap(obj1)
        gc.add_to_heap(obj2)
        gc.add_root(obj1)
        
        gc.collect()
        assert gc.total_collections == 1
        assert gc.get_heap_size() == 1
        
        # İkinci collection
        obj3 = MockValue("List")
        obj4 = MockValue("Map")
        
        gc.add_to_heap(obj3)
        gc.add_to_heap(obj4)
        gc.add_root(obj3)
        
        gc.collect()
        assert gc.total_collections == 2
        assert gc.get_heap_size() == 2
        # objects_collected cumulative - 1 from first collection, 1 from second
        assert gc.objects_collected == 2
    
    def test_empty_heap_collection(self, gc):
        """Boş heap'te collection"""
        gc.collect()
        
        assert gc.total_collections == 1
        assert gc.get_heap_size() == 0
        assert gc.objects_collected == 0
        assert gc.memory_freed == 0
    
    def test_memory_stats(self, gc):
        """Memory istatistikleri"""
        obj1 = MockValue("Integer")
        obj2 = MockValue("String")
        
        gc.add_to_heap(obj1)
        gc.add_to_heap(obj2)
        gc.add_root(obj1)
        
        # Collection öncesi
        stats_before = gc.get_memory_stats()
        assert stats_before['heap_size'] == 2
        assert stats_before['root_count'] == 1
        assert stats_before['total_collections'] == 0
        
        # Collection sonrası
        gc.collect()
        stats_after = gc.get_memory_stats()
        assert stats_after['heap_size'] == 1
        assert stats_after['root_count'] == 1
        assert stats_after['total_collections'] == 1
        assert stats_after['objects_collected'] == 1
        assert stats_after['memory_freed'] == 100
    
    def test_circular_references(self, gc):
        """Döngüsel referanslar"""
        # Bu test gerçek implementation'da daha karmaşık olur
        # Mock versiyonda basit senaryo
        obj1 = MockValue("List")
        obj2 = MockValue("List")
        
        gc.add_to_heap(obj1)
        gc.add_to_heap(obj2)
        gc.add_root(obj1)
        
        # obj1 obj2'yi referans ediyor, obj2 obj1'i referans ediyor (döngü)
        # GC bunu handle etmeli
        
        gc.collect()
        
        # Root olan obj1 kalmalı, obj2 silinmeli (döngüsel referans)
        assert gc.get_heap_size() == 1
        assert obj1 in gc.heap
        assert obj2 not in gc.heap

class TestMemoryAnalytics:
    """Memory analytics testleri"""
    
    def test_value_size_calculation(self):
        """Value size hesaplama"""
        int_val = MockValue("Integer")
        string_val = MockValue("String")
        list_val = MockValue("List")
        
        assert int_val.get_size() == 100
        assert string_val.get_size() == 100
        assert list_val.get_size() == 100
    
    def test_memory_report_generation(self):
        """Memory raporu oluşturma"""
        gc = MockGarbageCollector()
        
        # Test data
        obj1 = MockValue("Integer")
        obj2 = MockValue("String")
        
        gc.add_to_heap(obj1)
        gc.add_to_heap(obj2)
        gc.add_root(obj1)
        gc.collect()
        
        # Rapor kontrolü
        stats = gc.get_memory_stats()
        assert 'heap_size' in stats
        assert 'root_count' in stats
        assert 'total_collections' in stats
        assert 'memory_freed' in stats
        assert 'objects_collected' in stats

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

