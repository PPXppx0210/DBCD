from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .forms import UploadFileForm
from .models import User
from .models import OceanCurrentData
from django.contrib.auth import logout
import datetime
from .forms import SearchForm
from .forms import UserProfileForm
from .forms import AnalysisForm
from django.db.models import Avg, Max, Min, Variance, StdDev
import matplotlib.pyplot as plt
import io
import base64

def index(request):
    if request.method == 'POST':
        username = request.POST.get('user_name')
        password = request.POST.get('password')
        try:
            user = User.objects.get(Username=username)
            if check_password(password, user.Password):
                request.session['user_id'] = user.UserID
                return redirect('home')
            else:
                messages.error(request, '用户名或密码错误')
        except User.DoesNotExist:
            messages.error(request, '用户名或密码错误')

    return render(request, 'index.html')

def home(request):
    if 'user_id' not in request.session:
        return redirect('index')
    return render(request, 'home.html')

def formation(request):
    return render(request, 'formation.html')

def classification(request):
    return render(request, 'classification.html')

def impact(request):
    return render(request, 'impact.html')

def mainoc(request):
    return render(request, 'mainoc.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('inputUsername')
        password = request.POST.get('inputPassword')
        identity = request.POST.get('inputIdentity')
        name = request.POST.get('inputName')
        gender = request.POST.get('inputGender')
        id_card = request.POST.get('inputIDNumber')
        phone_number = request.POST.get('inputPhoneNumber')
        email = request.POST.get('inputEmail')
        
        hashed_password = make_password(password)
        
        # 创建新用户对象并保存到数据库中
        try:
            new_user = User(
                Username=username,
                Password=hashed_password,
                Identity=identity,
                Name=name,
                Gender=gender,
                IDCard=id_card,
                PhoneNumber=phone_number,
                Email=email
            )
            new_user.save()
            return render(request, 'register.html', {'user_registered': True})
        except Exception as e:
            messages.error(request, f'注册失败: {e}')

    return render(request, 'register.html', {'user_registered': False})

def personal(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, '请先登录')
        return redirect('index')

    try:
        custom_user = User.objects.get(UserID=user_id)
    except User.DoesNotExist:
        messages.error(request, '用户不存在')
        return redirect('index')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=custom_user)
        if form.is_valid():
            form.save()
            messages.success(request, '个人信息更新成功')
            return redirect('personal')
    else:
        form = UserProfileForm(instance=custom_user)

    return render(request, 'personal.html', {'form': form, 'user': custom_user})

def user_logout(request):
    logout(request)
    return redirect('index')

def parse_float(value):
    try:
        return float(value)
    except ValueError:
        return None

def handle_uploaded_file(file):
    lines = file.read().decode('utf-8').splitlines()
    year = 2023  # 默认年份
    month = 7    # 默认月份
    
    for line in lines:       
        station = line[0:15].strip()
        day = line[15:19].strip()
        time = line[20:23].strip()
        lat_str = line[23:29].strip()
        lat_dir = lat_str[-1]
        lat = parse_float(lat_str[:-1]) * (1 if lat_dir == 'N' else -1)
        long_str = line[29:36].strip()
        long_dir = long_str[-1]
        long = parse_float(long_str[:-1]) * (1 if long_dir == 'E' else -1)
        visibility = parse_float(line[37:43].strip())
        air_temperature = parse_float(line[44:50].strip())
        wind_direction = parse_float(line[51:57].strip())
        wind_speed = parse_float(line[58:64].strip())
        air_pressure = parse_float(line[65:71].strip())
        precipitation = parse_float(line[71:77].strip())
        sea_temperature = parse_float(line[78:83].strip())
        wind_wave_height = parse_float(line[84:89].strip())
        wind_wave_period = parse_float(line[90:95].strip())
        surge_height = parse_float(line[96:101].strip())
        surge_period = parse_float(line[102:107].strip())

        try:
            date_str = f"{year}{month:02d}{day}"
            date = datetime.datetime.strptime(date_str, '%Y%m%d').date()
            time = datetime.time(int(time), 0)

            OceanCurrentData.objects.create(
                station=station,
                date=date,
                time=time,
                latitude=lat,
                longitude=long,
                visibility=visibility,
                air_temperature = air_temperature,
                wind_direction=wind_direction,
                wind_speed=wind_speed,
                air_pressure=air_pressure,
                sea_temperature=sea_temperature,
                wind_wave_height=wind_wave_height,
                wind_wave_period=wind_wave_period
            )

        except Exception as e:
            print(f"Error saving data: {e}")

def dataimport(request):
    upload_success = None
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                handle_uploaded_file(request.FILES['file'])
                upload_success = True
            except Exception as e:
                upload_success = False
    else:
        form = UploadFileForm()
    return render(request, 'dataimport.html', {'form': form, 'upload_success': upload_success})

def datasearch(request):
    results = None
    station_description = ""
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if 'delete' in request.POST:
            try:
                data_id = request.POST.get('data_id')
                data_to_delete = OceanCurrentData.objects.get(CurrentID=data_id)
                data_to_delete.delete()
                messages.success(request, '数据已成功删除')
                return redirect('datasearch')
            except OceanCurrentData.DoesNotExist:
                messages.error(request, '删除失败：找不到相应数据')
        elif form.is_valid():
            station = form.cleaned_data['station']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            try:
                results = OceanCurrentData.objects.get(station=station, date=date, time=time)
                if station == "DSN":
                     station_description = (
                        "东山站背靠东山岛苏峰山，面向台湾海峡南部开阔水域，处于东海、南海交界点，作为物质交换的关键通道，物种丰富；"
                        "这里是省级珊瑚自然保护区，具有中国沿岸少有的原生态海洋生态系统；还是典型的亚热带季风气候区，台风、暴雨事件频发。"
                        "东山站附近的洋流主要受黑潮和东海沿岸流影响，"
                        "黑潮是北太平洋副热带西部的一支强劲暖流，从台湾东侧沿岸向东北方向流动，黑潮的分支也会影响到东海及其附近海域；"
                        "东海沿岸流是一股沿着中国东海岸线向北流动的海流，受季风影响显著。"
                        "洋流的温度对大气温度有直接影响，黑潮是一股暖流，其存在会提升周边大气温度；"
                        "洋流的流动方向和速度会受到风向和风速的影响，东亚季风对东海和南海的洋流都有显著影响。冬季北风增强会加速南向的沿岸流，夏季南风则会增强北向流动。"
                        )
                elif station == "LYG":
                    station_description = (
                        "连云港位于中国东部沿海，属于黄海和东海交界处，洋流受到多方面的影响。"
                        "黄海暖流是一股从南向北流动的暖流，主要受东海黑潮的影响，流经黄海中部;"
                        "而从东海流向黄海的沿岸流，在冬季通常是从北向南流动，夏季则从南向北流动。"
                        "黄海暖流带来的暖水对沿海大气温度有显著影响，会提高连云港及周边地区的气温。"
                        "季风对该地区的洋流影响显著，冬季盛行北风，导致沿岸流向南；夏季盛行南风，导致沿岸流向北。"
                        )
                elif station == "SSN":
                    station_description = (
                        "嵊山站位于中国东海舟山群岛附近，处于东海和近海洋流交汇处。"
                        "黑潮是一股强大的暖流，沿着台湾东部北上，并向东北方向流动。其分支会进入东海，影响舟山群岛附近的洋流；"
                        "东海沿岸流沿着中国东海岸线流动，通常向北方向流动，但受到季风影响会有变化。"
                        "黑潮及其分支的存在会提升嵊山及周边地区的海水温度，从而影响大气温度；尤其在冬季，暖流可以缓解冷空气带来的降温效应。"
                        )
                elif station == "XCS":
                    station_description = (
                        "小长山海洋站地处黄海北部，四面环海，距最近的陆地皮口港25千米。"
                        "黄海暖流从南向北流动，尤其在冬季，它沿着中国沿海向北流动，并对黄海北部的水文条件产生显著影响。"
                        "冬季冷空气南下时，尽管有暖流的缓和作用，气温仍会下降，但幅度可能比内陆地区要小。"
                        )
                else :
                    station_description = "暂无站点介绍..."
            except OceanCurrentData.DoesNotExist:
                messages.error(request, '找不到相应数据!')
    else:
        form = SearchForm()
    return render(request, 'datasearch.html', {'form': form, 'results': results, 'station_description': station_description})

def edit_data(request, data_id):
    data = OceanCurrentData.objects.get(CurrentID=data_id)
    if request.method == 'POST':
        field = request.POST.get('field')
        value = request.POST.get('value')
        setattr(data, field, value)
        data.save()
        messages.success(request, '数据已成功修改')
        return redirect('datasearch')
    fields = OceanCurrentData._meta.get_fields()
    return render(request, 'edit_data.html', {'data': data, 'fields': fields})

def plot_to_image():
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    image_png = buf.getvalue()
    buf.close()
    return base64.b64encode(image_png).decode('utf-8')

def dataanalyse(request):
    analysis_results = None
    plot_url = None
    if request.method == 'POST':
        form = AnalysisForm(request.POST)
        if form.is_valid():
            station = form.cleaned_data['station']
            dimension = form.cleaned_data['dimension']
            date = form.cleaned_data.get('date')
            month = form.cleaned_data.get('month')

            if date:
                data = OceanCurrentData.objects.filter(station=station, date=date).values_list('time', dimension)
                times = [item[0].strftime("%H:%M") for item in data]
                values = [item[1] for item in data]
                plt.figure()
                plt.plot(times, values)
                plt.xlabel('Time')
                plt.ylabel(dimension)
                plt.title(f'{dimension} on {date} at {station}')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()  # Ensure everything fits without overlapping
                plot_url = plot_to_image()

            elif month:
                start_date = datetime.date(month.year, month.month, 1)
                next_month = start_date + datetime.timedelta(days=31)
                end_date = next_month.replace(day=1) - datetime.timedelta(days=1)
                data = OceanCurrentData.objects.filter(station=station, date__range=(start_date, end_date)).values('date').annotate(avg_value=Avg(dimension))
                dates = [item['date'] for item in data]
                values = [item['avg_value'] for item in data]
                plt.figure()
                plt.plot(dates, values)
                plt.xlabel('Date')
                plt.ylabel(dimension)
                plt.title(f'Average {dimension} in {start_date.strftime("%Y-%m")} at {station}')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()  # Ensure everything fits without overlapping
                plot_url = plot_to_image()

            data = OceanCurrentData.objects.filter(station=station).values_list(dimension, flat=True)
            if data.exists():
                analysis_results = {
                    'average': data.aggregate(Avg(dimension))[f'{dimension}__avg'],
                    'max': data.aggregate(Max(dimension))[f'{dimension}__max'],
                    'min': data.aggregate(Min(dimension))[f'{dimension}__min'],
                    'variance': data.aggregate(Variance(dimension))[f'{dimension}__variance'],
                    'std_dev': data.aggregate(StdDev(dimension))[f'{dimension}__stddev'],
                }
            else:
                messages.error(request, '找不到相应数据!')
    else:
        form = AnalysisForm()
    return render(request, 'dataanalyse.html', {'form': form, 'analysis_results': analysis_results, 'plot_url': plot_url})