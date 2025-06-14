import { createClient } from '@supabase/supabase-js';

const isBrowser = typeof window !== 'undefined';

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  {
    auth: {
      flowType: 'pkce',
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: false,
      storage: isBrowser
        ? {
            getItem: (key) => sessionStorage.getItem(key),
            setItem: (key, value) => sessionStorage.setItem(key, value),
            removeItem: (key) => sessionStorage.removeItem(key),
          }
        : undefined, 
    },
  }
);
