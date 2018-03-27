Name: tsubame
Version: 0.1.1
Release: 1%{?dist}
Summary: Tsubame is a flexible Twitter client.	

License: GPLv3+
URL: https://github.com/m4rtinK/tsubame
Source0: tsubame-%s{version}.tar.gz

BuildArch: noarch
BuildRequires: python3-devel
BuildRequires: make
Requires: pyotherside
Requires: qt5-qtdeclarative-devel
Requires: qt5-qtquickcontrols2

%description
Tsubame is a flexible multi account & multi stream Twitter client.

%prep
%setup -q -n tsubame-%{version}


%build
make


%install
%make_install


%files
/usr/share/applications/*
/usr/share/icons/hicolor/128x128/apps/*
/usr/share/icons/hicolor/256x256/apps/*

%doc README.rst
%license COPYING.txt

%changelog

