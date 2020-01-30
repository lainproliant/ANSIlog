pkgbase='python-ansilog'
pkgname=('python-ansilog')
_module='ansilog'
pkgver='1.4'
pkgrel=1
pkgdesc="Smart and colorful solution for logging, output, and basic terminal control."
url="https://github.com/lainproliant/ansilog"
depends=('python')
makedepends=('python-setuptools')
license=('BSD')
arch=('any')
source=("https://files.pythonhosted.org/packages/source/${_module::1}/$_module/$_module-$pkgver.tar.gz")
sha256sums=('5b99f98486591581492f3f17b02feeed5c278bd07b7db79f3676ad45b36d318b')

build() {
    cd "${srcdir}/${_module}-${pkgver}"
    python setup.py clean --all
    python setup.py build
}

package() {
    depends+=()
    cd "${srcdir}/${_module}-${pkgver}"
    python setup.py install --root="${pkgdir}" --optimize=1 --skip-build
    install -Dm644 "$srcdir/${_module}-${pkgver}/LICENSE" "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
}
