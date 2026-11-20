const BASE='http://127.0.0.1:8000';
export const getToken=()=>localStorage.getItem('finance_token');
export const setToken=t=>localStorage.setItem('finance_token',t);
export const logout=()=>localStorage.removeItem('finance_token');
export async function api(path,options={}){const headers={'Content-Type':'application/json',...(options.headers||{})};if(getToken())headers.Authorization=`Bearer ${getToken()}`;const r=await fetch(BASE+path,{...options,headers});const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.detail||'Request failed');return d;}
