# Maintainer: Lain Musgrove <lain.proliant@gmail.com>
pkgbase='python-ansilog'
pkgname=('python-ansilog')
_module='ansilog'
pkgver='1.2'
pkgrel=1
pkgdesc="Smart and colorful solution for logging, output, and basic terminal control."
url="https://github.com/lainproliant/ansilog"
license=('BSD')
arch=('any')
source=("https://files.pythonhosted.org/packages/source/${_module::1}/$_module/$_module-$pkgver.tar.gz")
sha256sums=('893233ad88832a11fc4d467b85c0cf2393d410ee1325c6897aa8c7f31c4016fe')

build() {
    cd "${srcdir}/${_module}-${pkgver}"
    python setup.py build
}

package() {
    depends+=()
    cd "${srcdir}/${_module}-${pkgver}"
    python setup.py install --root="${pkgdir}" --optimize=1 --skip-build
    install -Dm644 LICENSE "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
}
