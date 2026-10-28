// Preloaded into every process when ENABLE_VOLUME_PERMS_SHIM=true (see start.sh).
//
// RunPod network volumes (NFS / FUSE) refuse chmod and chown with "Operation not permitted",
// even for root. Many tools treat that as fatal although the file itself was written fine:
// `git clone` and `git config` abort ("chmod on .git/config.lock failed"), and cp -a, tar, rsync
// and Python's shutil.copy* print errors. On such filesystems the mode and owner can't be
// changed anyway, so this reports success instead of EPERM there. Every other error, and every
// other filesystem (the container disk), behaves as usual.

#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/vfs.h>
#include <unistd.h>

static int is_network_fs(long type)
{
	switch ((unsigned long)type & 0xffffffffUL) {
	case 0x6969UL:		// NFS
	case 0x65735546UL:	// FUSE (MooseFS, virtiofs, ...)
	case 0xff534d42UL:	// CIFS
	case 0xfe534d42UL:	// SMB2
	case 0x00c36400UL:	// Ceph
	case 0x01021997UL:	// 9p
		return 1;
	}
	return 0;
}

// Only root's EPERM is the filesystem's doing; for other users it means "not your file".
static int ignore_path(int err, int dirfd, const char *path)
{
	struct statfs s;
	int r;

	if (err != EPERM || geteuid() != 0 || !path)
		return 0;
	if (path[0] == '/' || dirfd == AT_FDCWD)
		r = statfs(path, &s);
	else
		r = fstatfs(dirfd, &s);
	return r == 0 && is_network_fs(s.f_type);
}

static int ignore_fd(int err, int fd)
{
	struct statfs s;

	if (err != EPERM || geteuid() != 0)
		return 0;
	return fstatfs(fd, &s) == 0 && is_network_fs(s.f_type);
}

#define REAL(name) static __typeof__(name) *real; \
	if (!real) real = (__typeof__(name) *)dlsym(RTLD_NEXT, #name)

#define RETURN(ret, ignore) do { \
	int saved = errno; \
	if ((ret) != 0 && (ignore)) { errno = saved; return 0; } \
	errno = saved; return (ret); \
} while (0)

int chmod(const char *path, mode_t mode)
{
	REAL(chmod);
	int ret = real(path, mode);
	RETURN(ret, ignore_path(errno, AT_FDCWD, path));
}

int fchmod(int fd, mode_t mode)
{
	REAL(fchmod);
	int ret = real(fd, mode);
	RETURN(ret, ignore_fd(errno, fd));
}

int fchmodat(int dirfd, const char *path, mode_t mode, int flags)
{
	REAL(fchmodat);
	int ret = real(dirfd, path, mode, flags);
	RETURN(ret, ignore_path(errno, dirfd, path));
}

int chown(const char *path, uid_t uid, gid_t gid)
{
	REAL(chown);
	int ret = real(path, uid, gid);
	RETURN(ret, ignore_path(errno, AT_FDCWD, path));
}

int lchown(const char *path, uid_t uid, gid_t gid)
{
	REAL(lchown);
	int ret = real(path, uid, gid);
	RETURN(ret, ignore_path(errno, AT_FDCWD, path));
}

int fchown(int fd, uid_t uid, gid_t gid)
{
	REAL(fchown);
	int ret = real(fd, uid, gid);
	RETURN(ret, ignore_fd(errno, fd));
}

int fchownat(int dirfd, const char *path, uid_t uid, gid_t gid, int flags)
{
	REAL(fchownat);
	int ret = real(dirfd, path, uid, gid, flags);
	RETURN(ret, ignore_path(errno, dirfd, path));
}
