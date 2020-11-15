import json

from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib import messages
from py2neo import Graph,  Node, Relationship, NodeMatcher
from py2neo.matching import RelationshipMatcher
from adminuser.models import AdminUser, EntityType, RelationType
from user.models import User


# 管理员登录
def adminLogin(request):
    if request.method == 'GET':
        if 'adminname' in request.COOKIES:
            username = request.COOKIES.get('adminname')
            password = request.COOKIES.get('adminpassword')
            checked = 'checked'
        else:
            username = ''
            password = ''
            checked = ''
        return render(request, 'admin_login.html', {'adminname': username, 'adminpassword': password, 'checked': checked})
    else:
        # 接收数据
        username = request.POST.get('adminname')
        password = request.POST.get('adminpassword')

        # 校验数据
        if not all([username, password]):
            return render(request, 'admin_login.html', {'errmsg': '数据不完整'})

        # 业务处理:登录校验
        user = AdminUser.objects.filter(admin_name=username, admin_password=password).first()
        # 用户名密码正确
        if user is not None:
            print('找到了')

            # 获取登录后所要跳转到的地址
            # 默认跳转到首页
            next_url = request.GET.get('next', reverse('adminuser:adminIndex'))

            # 跳转到next_url
            response = redirect(next_url)  # HttpResponseRedirect

            # 判断是否需要记住用户名

            # 记住用户名
            response.set_cookie('adminname', username, max_age=7 * 24 * 3600)
            response.set_cookie('adminpassword', password, max_age=7 * 24 * 3600)
            print('记住了')

            # 返回response
            return response
        else:
            # 用户名或密码错误
            return render(request, 'admin_login.html', {'errmsg': '用户名或密码错误'})

# 连接neo4j
g = Graph('bolt://localhost:7687', password='neo4j123')
print('连接成功')
entitytypes = EntityType.objects.all()
relationtypes = RelationType.objects.all()
entity_map = {'煤矿特有事物':'PRO', '气体':'GAS', '设备':'EQU', '组织机构':'ORG', '人员':'PER', '参数值':'PAR', '采煤方法':'METHOD',
              '采煤工艺':'CRAFT', '爆炸事故':'EXP_ACCI', '水灾':'FLOOD_ACCI', '机电事故':'ELEC_ACCI', '火灾':'FIRE_ACCI', '支护事故':'ZHIHU_ACCI', '时间':'TIME',
              }

# 显示首页
def adminIndex(request):
    username = request.COOKIES.get('adminname')
    if username:
        print('ok')
        return render(request, 'admin_index.html', {'adminname':username})
    else:
        print('error')
        return redirect(reverse('adminuser:adminlogin'))

# 关系查询:实体1
def findRelationByEntity1(entity_type1, entity1):
    r = 'match (n:' + entity_type1 + '{name:"' + entity1 + '"}) -[r]-> (m) return n,r,m'
    # answer = g.run("MATCH (n:" + entity_type1 + " {name:\""+entity1+"\"})- [r] -> (m) RETURN n,r,m" )
    answer = g.run(r).data()
    # answer = g.run(r).to_subgraph()
    # 获取子图中所有节点对象并打印
    # nodes = sub_graph.nodes
    # for node in nodes:
    #     print(node)

    result_answer = json.dumps(answer, ensure_ascii=False)
    return result_answer

# 关系查询:实体1+关系
def findOtherEntities1(entity_type1, entity1, relation):
    answer = g.run("MATCH (n:" + entity_type1 + " {name:\"" + entity1 + "\"})-[r:" + relation + "]->(m) RETURN n,r,m").data()
    result_answer = json.dumps(answer, ensure_ascii=False)
    return result_answer

# 关系查询 整个知识图谱体系
def zhishitupu():
    answer = g.run("MATCH (n)- [r] -> (m) RETURN n,r,m ").data()
    return answer
# 关系查询：实体2
def findRelationByEntity2(entity_type2, entity2):
    answer = g.run("MATCH (n1)- [r] -> (n2:" + entity_type2 + " {name:\""+entity2+"\"}) RETURN n1,r,n2" ).data()
    result_answer = json.dumps(answer, ensure_ascii=False)
    return result_answer

# 关系查询：实体2+关系
def findOtherEntities2(entity_type2, entity2, relation):
    answer = g.run("MATCH (n1)- [r:" + relation + "] -> (n2:" + entity_type2 + " {name:\""+entity2+"\"}) RETURN n1,r,n2" ).data()
    result_answer = json.dumps(answer, ensure_ascii=False)
    return result_answer

def findEntity1toEntity2(entity_type1, entity1, relation, entity_type2, entity2):
    answer = g.run("MATCH (n1:" + entity_type1 + " {name:\"" + entity1 + "\"})- [r:" + relation + "] -> (n2:" + entity_type2 + " {name:\"" + entity2 + "\"}) RETURN n1,r,n2").data()
    result_answer = json.dumps(answer, ensure_ascii=False)
    return result_answer

# 知识库查询
def knowledgebase(request):
    if request.method == 'GET':
        return render(request, 'searchkb.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})
    else:
        entity1 = request.POST.get('entity_name1')
        entity_type1 = request.POST.get('entity_type1')
        relation = request.POST.get('relation_type')
        entity2 = request.POST.get('entity_name2')
        entity_type2 = request.POST.get('entity_type2')
        entity_label1 = ''
        entity_label2 = ''
        searchResult = {}
        for key in entity_map:
            if key == entity_type1:
                entity_label1 = entity_map[key]
            if key == entity_type2:
                entity_label2 = entity_map[key]

        # 若只输入entity1,则输出与entity1有直接关系的实体和关系
        if entity1 != '' and relation == '' and entity2 =='':
            # 判断节点是否存在
            matcher = NodeMatcher(g)
            node1 = matcher.match(entity_label1, name=entity1).first()
            if node1 is None:
                messages.error(request, '节点不存在')
                return render(request, 'searchkb.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})

            searchResult = findRelationByEntity1(entity_label1, entity1)
            searchResult = json.loads(searchResult) # 转换为字典
            # searchResult = list(searchResult)
            print(searchResult)

            # 如果节点不是孤立的,输出以该节点为起点的，有与之相关的节点和关系
            if len(searchResult) > 0:
                data = []
                links = []
                source_name = entity1
                node = {'name': source_name, 'des': source_name, 'symbolSize': 70, 'category': 0}
                data.append(node)
                for res in searchResult:
                    target_name = res['m']['name']
                    node = {'name': target_name, 'des': target_name, 'symbolSize': 50, 'category': 1}
                    data.append(node)

                    source = res['n']['name']
                    relation_name = res['r']['name']
                    rel = {'target':target_name, 'source':source, 'name':relation_name, 'des':relation_name}
                    links.append(rel)

                print(data)
                print(links)

                # data = [{'name': '中国科学院计算技术研究所', 'des': '中国科学院计算技术研究所', 'symbolSize': 70, 'category': 0, }, {'name': '徐志伟', 'des': '徐志伟', 'symbolSize': 50, 'category': 1, }, {'name': '文继荣', 'des': '文继荣', 'symbolSize': 50, 'category': 1, },
                #         {'name': '钮心忻', 'des': '钮心忻', 'symbolSize': 50, 'category': 1, }, ]
                # links = [{'target': '中国科学院计算技术研究所', 'source': '徐志伟', 'name': '属于', 'des': '作者-作者单位'}, {'target': '中国科学院计算技术研究所', 'source': '文继荣', 'name': '属于', 'des': '作者-作者单位'},
                #          {'target': '中国科学院计算技术研究所', 'source': '钮心忻', 'name': '属于', 'des': '作者-作者单位'}, ]

                return render(request, 'searchkb.html', {'data':json.dumps(data),'link':json.dumps(links),
                                                     'entity1':entity1, 'entity_type1':entity_type1, 'relation':relation,
                                                     'entity2':entity2, 'entity_type2':entity_type2,
                                                   'entitytypes': entitytypes, 'relationtypes':relationtypes})
            # 节点是孤立的,只返回节点
            elif len(searchResult) == 0:
                data = []
                links = []
                source_name = entity1
                node = {'name': source_name, 'des': source_name, 'symbolSize': 70, 'category': 0}
                data.append(node)

                return render(request, 'searchkb.html', {'data': json.dumps(data), 'link': json.dumps(links),
                                                         'entity1': entity1, 'entity_type1': entity_type1,
                                                         'relation': relation,
                                                         'entity2': entity2, 'entity_type2': entity_type2,
                                                         'entitytypes': entitytypes, 'relationtypes': relationtypes})


        # 若只输入entity2则,则输出与entity2有直接关系的实体和关系
        if entity1 == '' and relation == '' and entity2 !='':
            # 判断节点是否存在
            matcher = NodeMatcher(g)
            node2 = matcher.match(entity_label2, name=entity2).first()
            if node2 is None:
                messages.error(request, '节点不存在')
                return render(request, 'searchkb.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})

            searchResult = findRelationByEntity2(entity_label2, entity2)
            searchResult = json.loads(searchResult) # 转换为字典
            print(searchResult)

            # 如果节点不是孤立的,输出以该节点为终点的，有与之相关的节点和关系
            if (len(searchResult) > 0):
                data = []
                links = []
                target_name = entity2
                node = {'name': target_name, 'des': target_name, 'symbolSize': 70, 'category': 0}
                data.append(node)
                for res in searchResult:
                    source_name = res['n1']['name']
                    node = {'name': source_name, 'des': source_name, 'symbolSize': 50, 'category': 1}
                    data.append(node)

                    source = res['n1']['name']
                    relation_name = res['r']['name']
                    rel = {'target': target_name, 'source': source, 'name': relation_name, 'des': relation_name}
                    links.append(rel)

                print(data)
                print(links)

                # data = [{'name': '中国科学院计算技术研究所', 'des': '中国科学院计算技术研究所', 'symbolSize': 70, 'category': 0, }, {'name': '徐志伟', 'des': '徐志伟', 'symbolSize': 50, 'category': 1, }, {'name': '文继荣', 'des': '文继荣', 'symbolSize': 50, 'category': 1, },
                #         {'name': '钮心忻', 'des': '钮心忻', 'symbolSize': 50, 'category': 1, }, ]
                # links = [{'target': '中国科学院计算技术研究所', 'source': '徐志伟', 'name': '属于', 'des': '作者-作者单位'}, {'target': '中国科学院计算技术研究所', 'source': '文继荣', 'name': '属于', 'des': '作者-作者单位'},
                #          {'target': '中国科学院计算技术研究所', 'source': '钮心忻', 'name': '属于', 'des': '作者-作者单位'}, ]

                return render(request, 'searchkb.html', {'data': json.dumps(data), 'link': json.dumps(links),
                                                         'entity1': entity1, 'entity_type1': entity_type1,
                                                         'relation': relation,
                                                         'entity2': entity2, 'entity_type2': entity_type2,
                                                         'entitytypes': entitytypes, 'relationtypes': relationtypes})
                # 节点是孤立的,只返回节点
            elif len(searchResult) == 0:
                data = []
                links = []
                target_name = entity2
                node = {'name': target_name, 'des': target_name, 'symbolSize': 70, 'category': 0}
                data.append(node)

                return render(request, 'searchkb.html', {'data': json.dumps(data), 'link': json.dumps(links),
                                                         'entity1': entity1, 'entity_type1': entity_type1,
                                                         'relation': relation,
                                                         'entity2': entity2, 'entity_type2': entity_type2,
                                                         'entitytypes': entitytypes, 'relationtypes': relationtypes})


        # 若输入entity1和relation，则输出与entity1具有relation关系的其他实体
        if entity1 != '' and relation != '' and entity2 =='':
            # 判断节点是否存在
            matcher = NodeMatcher(g)
            node1 = matcher.match(entity_label1, name=entity1).first()
            if node1 is None:
                messages.error(request, '节点不存在')
                return render(request, 'searchkb.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})

            searchResult = findOtherEntities1(entity_label1, entity1, relation)
            searchResult = json.loads(searchResult)  # 转换为字典
            # print(searchResult)
            if (len(searchResult) > 0):
                data = []
                links = []
                source_name = entity1
                node = {'name': source_name, 'des': source_name, 'symbolSize': 70, 'category': 0}
                data.append(node)
                for res in searchResult:
                    target_name = res['m']['name']
                    node = {'name': target_name, 'des': target_name, 'symbolSize': 50, 'category': 1}
                    data.append(node)

                    source = res['n']['name']
                    relation_name = res['r']['name']
                    rel = {'target': target_name, 'source': source, 'name': relation_name, 'des': relation_name}
                    links.append(rel)

                print(data)
                print(links)

                # data = [{'name': '中国科学院计算技术研究所', 'des': '中国科学院计算技术研究所', 'symbolSize': 70, 'category': 0, }, {'name': '徐志伟', 'des': '徐志伟', 'symbolSize': 50, 'category': 1, }, {'name': '文继荣', 'des': '文继荣', 'symbolSize': 50, 'category': 1, },
                #         {'name': '钮心忻', 'des': '钮心忻', 'symbolSize': 50, 'category': 1, }, ]
                # links = [{'target': '中国科学院计算技术研究所', 'source': '徐志伟', 'name': '属于', 'des': '作者-作者单位'}, {'target': '中国科学院计算技术研究所', 'source': '文继荣', 'name': '属于', 'des': '作者-作者单位'},
                #          {'target': '中国科学院计算技术研究所', 'source': '钮心忻', 'name': '属于', 'des': '作者-作者单位'}, ]

                return render(request, 'searchkb.html', {'data': json.dumps(data), 'link': json.dumps(links),
                                                         'entity1': entity1, 'entity_type1': entity_type1,
                                                         'relation': relation,
                                                         'entity2': entity2, 'entity_type2': entity_type2,
                                                         'entitytypes': entitytypes, 'relationtypes': relationtypes})
                # 节点是孤立的,只返回节点
            elif len(searchResult) == 0:
                data = []
                links = []
                source_name = entity1
                node = {'name': source_name, 'des': source_name, 'symbolSize': 70, 'category': 0}
                data.append(node)

                return render(request, 'searchkb.html', {'data': json.dumps(data), 'link': json.dumps(links),
                                                         'entity1': entity1, 'entity_type1': entity_type1,
                                                         'relation': relation,
                                                         'entity2': entity2, 'entity_type2': entity_type2,
                                                         'entitytypes': entitytypes, 'relationtypes': relationtypes})


        # 若输入entity2和relation，则输出与entity2具有relation关系的其他实体
        if entity1 == '' and relation != '' and entity2 !='':
            # 判断节点是否存在
            matcher = NodeMatcher(g)
            node2 = matcher.match(entity_label2, name=entity2).first()
            if node2 is None:
                messages.error(request, '节点不存在')
                return render(request, 'searchkb.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})

            searchResult = findOtherEntities2(entity_label2, entity2, relation)
            searchResult = json.loads(searchResult)  # 转换为字典
            # print(searchResult)
            if (len(searchResult) > 0):
                data = []
                links = []
                target_name = entity2
                node = {'name': target_name, 'des': target_name, 'symbolSize': 70, 'category': 0}
                data.append(node)
                for res in searchResult:
                    source_name = res['n1']['name']
                    node = {'name': source_name, 'des': source_name, 'symbolSize': 50, 'category': 1}
                    data.append(node)

                    source = res['n1']['name']
                    relation_name = res['r']['name']
                    rel = {'target': target_name, 'source': source, 'name': relation_name, 'des': relation_name}
                    links.append(rel)

                print(data)
                print(links)

                # data = [{'name': '中国科学院计算技术研究所', 'des': '中国科学院计算技术研究所', 'symbolSize': 70, 'category': 0, }, {'name': '徐志伟', 'des': '徐志伟', 'symbolSize': 50, 'category': 1, }, {'name': '文继荣', 'des': '文继荣', 'symbolSize': 50, 'category': 1, },
                #         {'name': '钮心忻', 'des': '钮心忻', 'symbolSize': 50, 'category': 1, }, ]
                # links = [{'target': '中国科学院计算技术研究所', 'source': '徐志伟', 'name': '属于', 'des': '作者-作者单位'}, {'target': '中国科学院计算技术研究所', 'source': '文继荣', 'name': '属于', 'des': '作者-作者单位'},
                #          {'target': '中国科学院计算技术研究所', 'source': '钮心忻', 'name': '属于', 'des': '作者-作者单位'}, ]

                return render(request, 'searchkb.html', {'data': json.dumps(data), 'link': json.dumps(links),
                                                         'entity1': entity1, 'entity_type1': entity_type1,
                                                         'relation': relation,
                                                         'entity2': entity2, 'entity_type2': entity_type2,
                                                         'entitytypes': entitytypes, 'relationtypes': relationtypes})
                # 节点是孤立的,只返回节点
            elif len(searchResult) == 0:
                data = []
                links = []
                target_name = entity2
                node = {'name': target_name, 'des': target_name, 'symbolSize': 70, 'category': 0}
                data.append(node)

                return render(request, 'searchkb.html', {'data': json.dumps(data), 'link': json.dumps(links),
                                                         'entity1': entity1, 'entity_type1': entity_type1,
                                                         'relation': relation,
                                                         'entity2': entity2, 'entity_type2': entity_type2,
                                                         'entitytypes': entitytypes, 'relationtypes': relationtypes})

        # 若全部输入，则输出一条具体关系
        if entity1 != '' and relation != '' and entity2 != '':
            # 判断节点是否存在
            matcher = NodeMatcher(g)
            node1 = matcher.match(entity_label1, name=entity1).first()
            node2 = matcher.match(entity_label2, name=entity2).first()
            if not all([node1, node2]):
                messages.error(request, '节点选择有误')
                return render(request, 'searchkb.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})

            searchResult = findEntity1toEntity2(entity_label1, entity1, relation, entity_label2, entity2)
            searchResult = json.loads(searchResult)  # 转换为字典
            # print(searchResult)
            if (len(searchResult) > 0):
                data = []
                links = []
                source_name = entity1
                node = {'name': source_name, 'des': source_name, 'symbolSize': 70, 'category': 0}
                data.append(node)
                for res in searchResult:
                    source_name = res['n1']['name']
                    target_name = res['n2']['name']
                    node2 = {'name': target_name, 'des': target_name, 'symbolSize': 50, 'category': 1}
                    data.append(node2)
                    relation_name = res['r']['name']
                    rel = {'target': target_name, 'source': source_name, 'name': relation_name, 'des': relation_name}
                    links.append(rel)

                print(data)
                print(links)

                # data = [{'name': '中国科学院计算技术研究所', 'des': '中国科学院计算技术研究所', 'symbolSize': 70, 'category': 0, }, {'name': '徐志伟', 'des': '徐志伟', 'symbolSize': 50, 'category': 1, }, {'name': '文继荣', 'des': '文继荣', 'symbolSize': 50, 'category': 1, },
                #         {'name': '钮心忻', 'des': '钮心忻', 'symbolSize': 50, 'category': 1, }, ]
                # links = [{'target': '中国科学院计算技术研究所', 'source': '徐志伟', 'name': '属于', 'des': '作者-作者单位'}, {'target': '中国科学院计算技术研究所', 'source': '文继荣', 'name': '属于', 'des': '作者-作者单位'},
                #          {'target': '中国科学院计算技术研究所', 'source': '钮心忻', 'name': '属于', 'des': '作者-作者单位'}, ]

                return render(request, 'searchkb.html', {'data': json.dumps(data), 'link': json.dumps(links),
                                                         'entity1': entity1, 'entity_type1': entity_type1,
                                                         'relation': relation,
                                                         'entity2': entity2, 'entity_type2': entity_type2,
                                                         'entitytypes': entitytypes, 'relationtypes': relationtypes})
                # 节点是孤立的,只返回节点
            elif len(searchResult) == 0:
                messages.error(request, '关系不存在')
                return render(request, 'searchkb.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})

        # 全为空 则输出整个知识图谱
        # if entity1 == '' and relation == '' and entity2 =='':
        #     searchResult = zhishitupu()
        #     # searchResult = sortDict(searchResult)
        # # print(json.loads(json.dumps(searchResult)))
        # return render(request, 'searchkb.html', {'searchResult': json.dumps(searchResult, ensure_ascii=False),
        #                                          'entity1': entity1, 'entity_type1': entity_type1, 'relation': relation,
        #                                          'entity2': entity2, 'entity_type2': entity_type2,
        #                                          'entitytypes': entitytypes, 'relationtypes': relationtypes})

# 欢迎页
def welcome(request):
    return render(request, 'welcome.html')

# 添加实体
def addEntity(request):
    if request.method == 'GET':
        return render(request, 'addEntity.html', {'entitytypes':entitytypes})
    else:
        label = request.POST.get('fid')
        entity_name = request.POST.get('entityname')
        for key in entity_map:
            if key == label:
                entity_label = entity_map[key]

        matcher = NodeMatcher(g)
        result = matcher.match(entity_label, name=entity_name).first()
        if result is not None:
            print(result)
            messages.error(request, '节点已存在')
            return render(request, 'addEntity.html', {'entitytypes': entitytypes})
        else:
            node = Node(entity_label, name=entity_name)
            g.create(node)
            messages.success(request, '添加成功')
            return render(request, 'addEntity.html', {'entitytypes':entitytypes})

# 修改实体
def changeEntity(request):
    if request.method == 'GET':
        return render(request, 'changeEntity.html', {'entitytypes': entitytypes})
    else:
        origin_label = request.POST.get('origin_label')
        origin_name = request.POST.get('origin_name')
        change_label = request.POST.get('change_label')
        change_name = request.POST.get('change_name')
        for key in entity_map:
            if key == origin_label:
                origin_entity_label = entity_map[key]
            if key == change_label:
                change_entity_label = entity_map[key]
        matcher = NodeMatcher(g)
        try:
            node = matcher.match(origin_entity_label, name=origin_name).first()

            if node is None:
                messages.error(request, '节点不存在或输入有误')
                return render(request, 'changeEntity.html', {'entitytypes': entitytypes})
            print('执行语句前')

            r = 'match (n:' + origin_entity_label + ' {name:"' + origin_name + '"}) remove n:' + origin_entity_label + ' set n:' + change_entity_label + ', n.name="' + change_name + '"'
            g.run(r)
        except Exception as e:
            print(e)
            messages.error(request, '修改失败')
            return render(request, 'changeEntity.html', {'entitytypes': entitytypes})
        else:
            print('执行语句后')
            messages.success(request, '修改成功')
            return render(request, 'changeEntity.html', {'entitytypes': entitytypes})


# 删除实体
def deleteEntity(request):
    if request.method == 'GET':
        return render(request, 'deleteEntity.html', {'entitytypes': entitytypes})
    else:
        delete_label = request.POST.get('delentitytype')
        delete_name = request.POST.get('deletename')
        for key in entity_map:
            if key == delete_label:
                delete_entity_label = entity_map[key]
        matcher = NodeMatcher(g)
        try:
            node = matcher.match(delete_entity_label, name=delete_name).first()
            if node is None:
                messages.error(request, '节点不存在或输入有误')
                return render(request, 'deleteEntity.html', {'entitytypes': entitytypes})
            g.delete(node)
        except Exception as e:
            print(e)
            messages.error(request, '删除失败')
            return render(request, 'deleteEntity.html', {'entitytypes': entitytypes})
        else:
            messages.success(request, '删除成功')
            return render(request, 'deleteEntity.html', {'entitytypes': entitytypes})

# 添加关系
def addRelation(request):
    if request.method == 'GET':
        return render(request, 'addRelation.html', {'entitytypes': entitytypes, 'relationtypes':relationtypes})
    else:
        s_entity_label = request.POST.get('s_entity_type')
        s_entity_name = request.POST.get('s_entityname')
        e_entity_label = request.POST.get('e_entity_type')
        e_entity_name = request.POST.get('e_entityname')
        relation_label = request.POST.get('relation_type')
        relation_name = request.POST.get('relationname')
        for key in entity_map:
            if key == s_entity_label:
                start_entity_label = entity_map[key]
            if key == e_entity_label:
                end_entity_label = entity_map[key]
        matcher = NodeMatcher(g)
        try:
            s_node = matcher.match(start_entity_label, name=s_entity_name).first()
            e_node = matcher.match(end_entity_label, name=e_entity_name).first()
            if not all([s_node, e_node]):
                messages.error(request, '节点选择有误')
                return render(request, 'addRelation.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})
            properties = {'name': relation_name}
            relate = Relationship(s_node, relation_label, e_node, **properties)
            g.merge(relate)
        except Exception as e:
            print(e)
            messages.error(request, '创建失败')
            return render(request, 'addRelation.html', {'entitytypes': entitytypes, 'relationtypes':relationtypes})
        else:
            messages.success(request, '创建成功')
            return render(request, 'addRelation.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})

# 修改关系
def changeRelation(request):
    if request.method == 'GET':
        return render(request, 'changeRelation.html', {'entitytypes': entitytypes, 'relationtypes':relationtypes})
    else:
        s_entity_label = request.POST.get('s_entity_type')
        s_entity_name = request.POST.get('s_entityname')
        e_entity_label = request.POST.get('e_entity_type')
        e_entity_name = request.POST.get('e_entityname')
        origin_relation_label = request.POST.get('origin_relation_type')
        change_relation_label = request.POST.get('change_relation_type')
        relation_name = request.POST.get('relationname')
        for key in entity_map:
            if key == s_entity_label:
                start_entity_label = entity_map[key]
            if key == e_entity_label:
                end_entity_label = entity_map[key]
        matcher = NodeMatcher(g)
        try:
            s_node = matcher.match(start_entity_label, name=s_entity_name).first()
            e_node = matcher.match(end_entity_label, name=e_entity_name).first()
            if not all([s_node, e_node]):
                messages.error(request, '节点选择有误')
                return render(request, 'changeRelation.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})

            # result = g.match(nodes=[s_node, e_node], r_type=origin_relation_label)
            # if len(list(result)) == 0:
            #     messages.error(request, '关系不存在')
            #     return render(request, 'changeRelation.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})

            r = 'match (n:' + start_entity_label + ' {name:"' + s_entity_name + '"})-[r:' + origin_relation_label + ']->(m:' + end_entity_label + ' {name:"' + e_entity_name + '"}) create (n)-[r2:' + change_relation_label + ']->(m) set r2.name="' + relation_name + '" delete r'
            g.run(r)
        except Exception as e:
            print(e)
            messages.success(request, '修改失败')
            return render(request, 'changeRelation.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})
        else:
            messages.success(request, '修改成功')
            return render(request, 'changeRelation.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})

# 删除关系
def deleteRelation(request):
    if request.method == 'GET':
        return render(request, 'deleteRelation.html', {'entitytypes': entitytypes, 'relationtypes':relationtypes})
    else:
        s_entity_label = request.POST.get('s_entity_type')
        s_entity_name = request.POST.get('s_entityname')
        e_entity_label = request.POST.get('e_entity_type')
        e_entity_name = request.POST.get('e_entityname')
        delete_relation_type = request.POST.get('delete_relation_type')
        for key in entity_map:
            if key == s_entity_label:
                start_entity_label = entity_map[key]
            if key == e_entity_label:
                end_entity_label = entity_map[key]
        matcher = NodeMatcher(g)
        try:
            s_node = matcher.match(start_entity_label, name=s_entity_name).first()
            e_node = matcher.match(end_entity_label, name=e_entity_name).first()
            if not all([s_node, e_node]):
                messages.error(request, '节点选择有误')
                return render(request, 'deleteRelation.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})

            r = 'match (n:' + start_entity_label + ' {name:"' + s_entity_name + '"})-[r:' + delete_relation_type + ']->(m:' + end_entity_label + ' {name:"' + e_entity_name + '"})  delete r'
            g.run(r)
        except Exception as e:
            print(e)
            messages.success(request, '删除失败')
            return render(request, 'deleteRelation.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})
        else:
            messages.success(request, '删除成功')
            return render(request, 'deleteRelation.html', {'entitytypes': entitytypes, 'relationtypes': relationtypes})

# 用户列表
def userList(request):
    userlist = User.objects.all()
    return render(request, 'userlist.html', {'userlist':userlist})

# 删除用户
def deleteuser(request,user_id):
    try:
        User.objects.get(id=user_id).delete()
    except Exception as e:
        messages.error(request, '删除失败')
    else:
        messages.error(request, '删除成功')
        return redirect(reverse('adminuser:userlist'))

# 管理员个人信息显示
def adminInfo(request):
    username = request.COOKIES.get('adminname')
    password = request.COOKIES.get('adminpassword')

    if request.method == 'GET':
        return render(request, 'admininfo.html', {'adminname':username, 'adminpassword':password})
    else:
        name = request.POST.get('name')
        pwd = request.POST.get('pwd')

        AdminUser.objects.filter(admin_name=username, admin_password=password).update(admin_name=name, admin_password=pwd)
        next_url = request.GET.get('next', reverse('adminuser:admininfo'))

        # 跳转到next_url
        response = redirect(next_url)  # HttpResponseRedirect

        response.set_cookie('adminname', name, max_age=7 * 24 * 3600)
        response.set_cookie('adminpassword', pwd, max_age=7 * 24 * 3600)

        return response

# 退出登录
def adminlogout(request):
    return redirect(reverse('adminuser:adminlogin'))







