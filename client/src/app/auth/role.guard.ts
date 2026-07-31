import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

export function roleGuard(requiredRole: 'admin' | 'user'): CanActivateFn {
  return () => {
    const auth = inject(AuthService);
    const router = inject(Router);
    const user = auth.currentUser();

    if (!user) {
      router.navigate(['/login']);
      return false;
    }
    if (requiredRole === 'admin' && user.role !== 'admin') {
      router.navigate(['/']);
      return false;
    }
    return true;
  };
}