#!/bin/sh
# branch: stable, beta, unstable. default: stable
branch=${1:-stable}
# arch to check package. irrelevant for actual arch
arch=x86_64

pkg=google-talkplugin
specfile=$pkg.spec
sourceurl=http://dl.google.com/linux/talkplugin/rpm/stable/$arch/

set -e

case "$branch" in
	stable|beta|unstable)
		;;
	*)
		echo "$0: Unknown branch: $branch. Supported branches: stable, beta, unstable." >&2
		exit 1
		;;
esac

set -e

echo -n "Fetching latest version... "
t=$(mktemp)

wget -c $sourceurl/repodata/primary.xml.gz
zcat primary.xml.gz | perl -ne 'm{<name>google-talkplugin</name>} and m{<version epoch="0" ver="([\d.]+)" rel="(\d+)"/>} and print "$1 $2"' > $t

set -- $(sed -re "s,^.+-([^-]+)-([^-]+).$arch$,\1 \2," $t)

rm -f primary.xml.gz $t

ver=$1
rev=$2

echo "$ver-$rev"

specfile=google-talkplugin.spec
oldrev=$(awk '/^%define[ 	]+svnrev[ 	]+/{print $NF}' $specfile)
if [ "$oldrev" != "$rev" ]; then
	echo "Updating $specfile for $ver r$rev"
	sed -i -e "
		s/^\(%define[ \t]\+svnrev[ \t]\+\)[0-9]\+\$/\1$rev/
		s/^\(%define[ \t]\+state[ \t]\+\)[a-z]\+\$/\1$branch/
		s/^\(Version:[ \t]\+\)[.0-9]\+\$/\1$ver/
	" $specfile
	../builder -ncs -g $specfile || :
	../builder -ncs -5 $specfile
else
	echo "Already up to date"
fi
