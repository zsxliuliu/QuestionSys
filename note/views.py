from django.shortcuts import render,redirect
from django.urls import reverse
from note.models import Note
import re
# Create your views here.

# 新建笔记
def newNote(request):
        user = request.user
        user_id = user.id
        if request.method == 'GET':
                print(user_id)
                notes = Note.objects.filter(user_id=user_id).order_by('-create_time')
                return render(request, 'new_note.html',{'notes':notes})
        else:

                # 接收笔记数据
                title = request.POST.get('title')
                content = request.POST.get('content')

                # 校验数据
                if not all([title, content]):
                        return render(request, 'new_note.html', {'errmsg': '数据不完整'})

                # 进行业务处理: 进行笔记保存
                note = Note.objects.create(title=title, content=content, user_id=user_id)

                notes = Note.objects.filter(user_id=user_id).order_by('-create_time')
                return render(request, 'new_note.html', {'notes': notes})

def editnote(request, note_id):
        note_id = note_id
        user = request.user
        user_id = user.id
        if request.method == 'GET':
                note = Note.objects.get(note_id=note_id)
                noteslist = Note.objects.filter(user_id=user_id).order_by('-create_time')
                return render(request, 'edit_note.html', {'note':note,'noteslist':noteslist})
        else:
                # 接收笔记数据
                title = request.POST.get('title')
                content = request.POST.get('content')
                note = Note.objects.filter(note_id=note_id).update(title=title, content=content)
                return redirect(reverse('user:index'))







