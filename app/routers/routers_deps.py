from fastapi import APIRouter,Depends

router = APIRouter()

def level_1():
    print("level 1")
    return 10

def level_2a(t2a:int = Depends(level_1)):
    print("level 2a")
    return 20+t2a #20+10=30

def level_2b(t2b:int=Depends(level_1)):
    print("level 2b")
    return 40+t2b #40+10=50

def level_3(l2b:int =Depends(level_2b),l2a:int=Depends(level_2a))->int:
    print("level 3")
    return l2a+l2b #80

def query_depends(user:str,token:str):
    data={
        'user':user,
        'token':token
    }
    return data

@router.get('/deps')
async def level3(total:int=Depends(level_3),common:str=Depends(query_depends)):
    print("total")
    data = {
        'total':total,
        'common':common
    }
    return data