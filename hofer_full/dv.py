import re,json
def nuxt(h):
  a=json.loads(re.search(r'id="__NUXT_DATA__">(.*?)</script>',h,re.S).group(1))
  memo={}
  def r(i,depth=0):
    if not isinstance(i,int) or depth>60: return i
    if i in memo: return memo[i]
    v=a[i]
    if isinstance(v,list):
      if v and isinstance(v[0],str) and v[0] in('Reactive','ShallowReactive','Ref','ShallowRef','Set','Map','EmptyRef','Date') :
        o=r(v[1],depth+1) if len(v)>1 else None
      else: o=[r(x,depth+1) for x in v]
    elif isinstance(v,dict): o={k:r(x,depth+1) for k,x in v.items()}
    else: o=v
    memo[i]=o;return o
  return r(0)
def find_product(o):
  st=[o]
  while st:
    x=st.pop()
    if isinstance(x,dict):
      if 'sku' in x and 'ingredients' in x: return x
      st.extend(x.values())
    elif isinstance(x,list): st.extend(x)
