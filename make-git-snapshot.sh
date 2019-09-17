#!/bin/sh

# Usage: ./make-git-snapshot.sh [COMMIT]
#
# to make a snapshot of the given tag/branch.  Defaults to HEAD.
# Point env var REF to a local mesa repo to reduce clone time.

DIRNAME=igt-gpu-tools-$( date +%Y%m%d )

REF=${REF:+--reference $REF}
HEAD=${1:-HEAD}

echo REF ${REF:+--reference $REF}
echo DIRNAME $DIRNAME
echo HEAD $HEAD

rm -rf $DIRNAME
trap 'rm -rf $DIRNAME' EXIT

git clone ${REF:+--reference $REF} \
	https://gitlab.freedesktop.org/drm/igt-gpu-tools.git $DIRNAME

export GIT_DIR=$DIRNAME/.git

sed -i "igt-gpu-tools.spec" \
	-e "s/%global gitcommit [0-9a-f]\+/%global gitcommit $(git rev-parse $HEAD)/" \
	-e "s/%global gitdate [0-9]\+/%global gitdate $(date +%Y%m%d)/" \
	-e "s/^\(Release:\s\+\)[0-9]\+/\11/"

git archive --format=tar $HEAD | bzip2 > $DIRNAME.tar.bz2
