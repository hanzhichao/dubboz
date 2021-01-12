from dubboz import Dubbo, Service


def test_dubbo():
    dubbo = Dubbo('127.0.0.1', 20880)
    assert dubbo.get_services() == ['com.longteng.autotest.AnimalService']
    assert dubbo.get_methods('com.longteng.autotest.AnimalService') == ['getAnimalInfo', 'delAnimal', 'listAnimals',
                                                                        'addAnimal', 'updateAnimalInfo']
    assert dubbo.invoke('com.longteng.autotest.AnimalService', 'listAnimals') == ('[]', 0)


def test_service():
    service = Service('dubbo://127.0.0.1:20880', 'com.longteng.autotest.AnimalService')
    assert service.methods == ['getAnimalInfo', 'delAnimal', 'listAnimals', 'addAnimal', 'updateAnimalInfo']
    assert service.listAnimals() == '[]'
    assert service.call('listAnimals') == ('[]', 0)
    assert service.call_all('listAnimals') == [('[]', 0)]