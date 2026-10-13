import argparse,json,os,sys
from pathlib import Path
from .store import Store
from .providers import MemoryService

def main():
    p=argparse.ArgumentParser(description='Local Memory Merge prototype')
    p.add_argument('--data',default=os.getenv('MM_DATA',str(Path(__file__).resolve().parents[1]/'data')))
    sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('health'); sub.add_parser('flush'); sub.add_parser('demo'); sub.add_parser('rebuild')
    backup=sub.add_parser('backup'); backup.add_argument('target')
    w=sub.add_parser('web'); w.add_argument('--port',type=int,default=8765)
    for name in ['capture','remember','list','recall','rag','review','judge','index','link']:
        s=sub.add_parser(name); s.add_argument('--project',default='default')
        if name in {'capture','remember'}:
            s.add_argument('content'); s.add_argument('--source',required=True); s.add_argument('--event-id')
        if name=='remember': s.add_argument('--confirmed',action='store_true')
        if name in {'recall','rag'}: s.add_argument('query')
        if name in {'review','judge'}: s.add_argument('id')
        if name=='review': s.add_argument('action',choices=['approve','reject','forget'])
        if name=='list': s.add_argument('--status',choices=['pending','approved','rejected','deleted'])
        if name=='link': s.add_argument('a'); s.add_argument('b'); s.add_argument('relation',choices=['supports','contradicts','supersedes','related'])
    a=p.parse_args(); store=Store(a.data); service=MemoryService.from_env(store)
    if a.cmd=='web':
        from .web import make_server
        server=make_server(store,a.port); print(f'Mind graph: http://127.0.0.1:{server.server_port}',flush=True)
        try: server.serve_forever()
        except KeyboardInterrupt: pass
        finally: server.server_close()
        return
    if a.cmd=='health': result=store.health()
    elif a.cmd=='flush': result=store.flush()
    elif a.cmd=='rebuild': result=store.rebuild()
    elif a.cmd=='backup': result=store.backup(a.target)
    elif a.cmd=='demo':
        rows=[]
        for i,text in enumerate(['选择 SQLite 作为事务真源','Markdown 镜像支持人类审阅','自动记忆先进入待审队列','RAG 召回必须附带来源']):
            rows.append(store.capture('demo',text,'demo:synthetic',mode='manual',confirmed=True,event_id=str(i)))
        store.link('demo',rows[0]['id'],rows[1]['id'],'supports'); store.link('demo',rows[2]['id'],rows[3]['id'],'supports')
        result={'synthetic_memories':len(rows),'project':'demo'}
    elif a.cmd in {'capture','remember'}:
        result=store.capture(a.project,a.content,a.source,mode='manual' if a.cmd=='remember' else 'auto',confirmed=getattr(a,'confirmed',False),event_id=a.event_id)
    elif a.cmd=='list': result=store.list_memories(a.project,a.status)
    elif a.cmd=='recall': result=service.recall(a.project,a.query)
    elif a.cmd=='rag': result=service.rag(a.project,a.query)
    elif a.cmd=='review': result=store.review(a.project,a.id,a.action)
    elif a.cmd=='judge': result=service.judge(a.project,a.id)
    elif a.cmd=='index': result=service.index(a.project)
    elif a.cmd=='link': result=store.link(a.project,a.a,a.b,a.relation)
    store.flush(); print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
