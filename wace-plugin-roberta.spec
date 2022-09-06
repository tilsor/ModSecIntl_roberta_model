Name:           wace-plugin-roberta
Version:        1.0
Release:        1%{?dist}
Summary:        WACE plugin for roberta ML model.

License:        Apache v2.0
URL:            https://www.fing.edu.uy/inco/proyectos/wafmind
Source0:        %{name}-%{version}.tar.gz

BuildRequires: git
BuildRequires: golang
BuildRequires: protobuf-devel

Requires: wace

%description 
WACE is framework for adding machine learning capabilities to WAFs
(such as mod_security) and OWASP CRS. This package corresponds to the
machine learning plugin, which communicates with the roberta model.

%global debug_package %{nil}

%prep
%autosetup
go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.28.0
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.2.0

%build
export GOPATH=~/go
export PATH=$PATH:$GOPATH/bin

# This is only necessary as long as repos are private
go env -w GOPRIVATE=github.com/tilsor/ModSecIntl_logger
cat << EOF > /tmp/github-credentials.sh
#!/bin/bash
echo username=$GIT_USERNAME
echo password=$GIT_PASSWORD
EOF
git config --global credential.helper "/bin/bash /tmp/github-credentials.sh"

make

%install
install -Dpm 644 roberta.so %{buildroot}%{_libdir}/wace/plugins/model/roberta.so
# TODO: add a configuration file

%post

%files
%{_libdir}/wace/plugins/model/roberta.so
# %license LICENSE

%changelog
* Tue Sep 6 2022 Juan Diego Campo <jdcampo@fing.edu.uy>
- Initial release 1.0-1
